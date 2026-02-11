import re
import traceback
import cv2
import numpy as np
import os
from backend_fastapi.utils.LogManeger import log_info, log_error

class CaptchaSolver:
    """
    验证码识别工具类
    优先使用 EasyOCR，ddddocr 作为备选。
    """
    
    def __init__(self, task_id):
        self.task_id = task_id
        self.reader = None
        self.ocr = None
        self.ocr_old = None
        self.op_templates = []

        # 加载运算符模板库
        self._load_templates(self.task_id)

        # 初始化 EasyOCR (优先)
        try:
            import easyocr
            # gpu=False 保证在无显卡环境下的稳定性
            # verbose=False 关闭进度条日志
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            log_info(f"[{task_id}] 验证码识别模块 (EasyOCR) 初始化成功")
        except Exception as e:
            log_error(f"[{task_id}] EasyOCR 初始化失败: {str(e)}")

        # 初始化 ddddocr (备选)
        try:
            import ddddocr
            self.ocr = ddddocr.DdddOcr(show_ad=False)
            self.ocr_old = ddddocr.DdddOcr(show_ad=False, old=True)
            self.ocr_beta = ddddocr.DdddOcr(show_ad=False, beta=True)
            log_info(f"[{task_id}] 验证码识别模块 (ddddocr) 初始化成功 (Standard, Old, Beta)")
        except ImportError as e:
            log_error(f"[{task_id}] 验证码识别库导入失败 (ddddocr): {str(e)}")
        except Exception as e:
            log_error(f"[{task_id}] 验证码识别模块 (ddddocr) 初始化失败: {str(e)}")

    def _load_templates(self, task_id):
        """加载运算符模板图片，提取轮廓特征用于匹配"""
        # 获取当前文件所在目录 (backend_fastapi/utils)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录 (backend_fastapi/utils -> backend_fastapi -> root)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        template_files = [
            (os.path.join(project_root, "+.png"), "+"),
            (os.path.join(project_root, "-.png"), "-"),
            (os.path.join(project_root, "x.png"), "*"),
            (os.path.join(project_root, "c.png"), "/")
        ]
        
        for path, label in template_files:
            if not os.path.exists(path):
                log_info(f"[{task_id}] 模板文件不存在: {path}")
                continue
                
            try:
                img = cv2.imread(path)
                if img is None: continue
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Otsu 二值化
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    # 取最大轮廓
                    cnt = max(contours, key=cv2.contourArea)
                    self.op_templates.append({
                        'label': label,
                        'contour': cnt
                    })
                    log_info(f"[{task_id}] 加载运算符模板成功: {label}")
            except Exception as e:
                log_error(f"[{task_id}] 加载模板 {path} 失败: {e}")

    def _enhance_image(self, image_bytes, task_id):
        """
        图像预处理：增强对比度，二值化，以便更清晰地识别运算符
        """
        try:
            # 字节转 numpy 数组
            nparr = np.frombuffer(image_bytes, np.uint8)
            # 解码为图像
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return image_bytes

            # 1. 尝试去除噪点 (非局部均值去噪)
            # h=10 (强度), templateWindowSize=7, searchWindowSize=21
            denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

            # 2. 转灰度
            gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
            
            # 3. 自适应阈值二值化 (比固定阈值更适合光照/背景不均匀的情况)
            # blockSize=11, C=2
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # 4. 形态学操作：开运算去除微小噪点
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

            success, encoded_image = cv2.imencode('.png', opened)
            if success:
                return encoded_image.tobytes()
            return image_bytes
        except Exception as e:
            log_info(f"[{task_id}] 图像预处理失败，使用原图: {str(e)}")
            return image_bytes

    def _distinguish_plus_multiply(self, roi, task_id):
        """
        区分 + 和 * (x)
        策略 1: 霍夫变换检测直线角度
        策略 2: 像素网格分布 (Fallback)
        """
        try:
            h, w = roi.shape
            if h == 0 or w == 0: return '+'

            # 1. 霍夫直线检测
            # 放大图像以提高直线检测准确率
            scale = 4.0
            h_big = int(h * scale)
            w_big = int(w * scale)
            roi_big = cv2.resize(roi, (w_big, h_big), interpolation=cv2.INTER_CUBIC)
            
            # 确保是二值图
            _, binary_roi = cv2.threshold(roi_big, 127, 255, cv2.THRESH_BINARY)
            
            # Canny 边缘
            edges = cv2.Canny(binary_roi, 50, 150)
            
            # 参数调整：
            # threshold: 投票阈值，放大后可以稍微大一点，避免噪点
            # minLineLength: 至少 5 个像素 (更宽松)
            # threshold: 10 (更宽松)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=10, 
                                  minLineLength=5, maxLineGap=5)
            
            ortho_count = 0 # 正交线 (0, 90度) -> +
            diag_count = 0  # 对角线 (45, 135度) -> *
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angle = np.abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
                    # 归一化到 0-180
                    if angle > 180: angle -= 180
                    
                    # 修正角度判定范围
                    # 正交: 0(180)±10, 90±10
                    if (angle <= 10) or (angle >= 170) or (80 <= angle <= 100):
                        ortho_count += 1
                    # 对角: 45±15, 135±15
                    elif (30 <= angle <= 60) or (120 <= angle <= 150):
                        diag_count += 1
            
            # 添加task_id前缀
            log_info(f"[{task_id}] Hough Check (Scaled): Ortho={ortho_count}, Diag={diag_count}")
            
            # 只要检测到对角线，且对角线数量不显著少于正交线，就认为是 *
            # (因为 + 号很少会有长对角线，而 x 号可能有短正交线噪音)
            if diag_count > 0 and diag_count >= ortho_count * 0.5:
                return '*'
            
            # 如果正交线占主导，则是 +
            if ortho_count > diag_count:
                return '+'

            # 2. 像素网格分布 (Fallback)
            # 归一化大小到 30x30，使用最近邻插值保持二值特性
            resized = cv2.resize(roi, (30, 30), interpolation=cv2.INTER_NEAREST)
            
            blocks = []
            for r in range(3):
                for c in range(3):
                    block = resized[r*10:(r+1)*10, c*10:(c+1)*10]
                    blocks.append(np.count_nonzero(block)) # 使用 count_nonzero
            
            score_plus = blocks[1] + blocks[3] + blocks[5] + blocks[7]
            score_multiply = blocks[0] + blocks[2] + blocks[6] + blocks[8]
            
            # log_info(f"[{task_id}] Pixel Check: Score(+)={score_plus}, Score(*)={score_multiply}")
            
            # * 号通常有中心点 (block 4) 和角落，但也可能只有角落
            # + 号通常有中心点 (block 4) 和边缘中点
            
            # 如果角落像素显著多于边缘中点 -> *
            if score_multiply > score_plus * 1.1: 
                return '*'
            # 如果边缘中点像素显著多于角落 -> +
            elif score_plus > score_multiply * 1.1:
                return '+'
            else:
                return '+' # 默认 +

        except Exception as e:
            # log_error(f"[{task_id}] Plus/Multiply Check Error: {e}")
            return '+' # Default

    def identify_operator_cv(self, image_bytes, task_id):
        """
        使用 OpenCV 基于形态学特征识别运算符 (+, -, *, /)
        规则库基于样本分析：
        - Divide (/): 高而瘦 (h > 18, w/h < 0.6)
        - Plus (+): 高而宽 (h > 18, w/h > 0.8)
        - Minus (-): 扁平且矮 (h < 12)
        - Multiply (*): 中等大小 (12 <= h <= 18)
        """
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None: return None

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 自适应阈值二值化 (黑底白字)
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # 去噪
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

            # 查找轮廓
            # 使用 RETR_LIST 以便捕获所有轮廓，防止因为外框导致内部数字被忽略
            contours, _ = cv2.findContours(opened, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            # 按 x 坐标排序
            contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
            
            # 过滤小噪点和边框
            valid_items = []
            img_h, img_w = img.shape[:2]
            # log_info(f"[{task_id}] Image Size: w={img_w}, h={img_h}")
            
            for i, cnt in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cnt)
                # log_info(f"[{task_id}] Contour {i}: x={x}, y={y}, w={w}, h={h}") # Debug
                
                # 过滤全图边框
                if w > img_w * 0.9 and h > img_h * 0.9:
                    # log_info(f"[{task_id}]  Rejected: full border")
                    continue
                
                # 过滤噪点
                if h < 15: 
                    ar = w / float(h) if h > 0 else 0
                    # 1. 特殊处理减号 (-): 高度小但宽度适中，长宽比大
                    is_minus = (h > 3 and w > 8 and ar > 1.5)
                    # 2. 特殊处理小号的乘号/加号 (*|+): 虽然矮但呈方形 (例如 14x14)
                    is_small_op = (h > 10 and w > 10 and 0.8 < ar < 1.3)
                    
                    if is_minus or is_small_op:
                        pass # 保留可能是有效运算符的轮廓
                    else:
                        continue # 太矮且不符合特征
                
                if w > 60: 
                    continue # 太宽 (可能是干扰线)
                
                if w < 5 and h < 20: 
                    continue # 太细且不够高
                
                # 过滤掉位于最左边或最右边的干扰图形 (非数字区域)
                if x < 5 or x > img_w - 20:
                    continue

                valid_items.append((x, y, w, h, cnt))
            
            # 策略：寻找两个主要数字之间的元素
            # 1. 识别数字候选 
            # 规则：高度适中，纵横比正常 (0.2 < w/h < 1.5)，宽度不过大 (排除宽边框)
            digits = []
            for item in valid_items:
                x, y, w, h, cnt = item
                ar = w / float(h)
                # 宽度限制 < 60 (通常数字宽度在 20-30 左右，宽边框如 99+ 会被排除)
                # 高度限制 > 15 (排除 -, * 等小运算符)
                # 修正：允许高度稍小一点的数字 (12+)，以防止被误判为噪点
                if h > 12 and 8 < w < 60 and 0.2 < ar < 1.5:
                    digits.append(item)
            
            # 特殊情况：如果数字识别不足2个，尝试放宽条件（针对细长数字如1）
            if len(digits) < 2:
                for item in valid_items:
                    if item in digits: continue
                    x, y, w, h, cnt = item
                    ar = w / float(h)
                    # 针对数字 1 的放宽条件: 高度够高，宽度可以很窄
                    if h > 15 and w > 3 and ar < 0.5:
                        digits.append(item)
            
            # 如果找到多于2个数字，取面积最大的两个（假设是操作数）
            if len(digits) > 2:
                digits.sort(key=lambda x: x[2]*x[3], reverse=True)
                digits = digits[:2]
                digits.sort(key=lambda x: x[0]) # 重新按 x 排序

            op_candidate = None
            def get_solidity(cnt):
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                area = cv2.contourArea(cnt)
                return float(area)/hull_area if hull_area > 0 else 0

            def is_valid_op_candidate(item):
                """过滤掉实心度过高的噪点 (除非是扁平的减号)"""
                x, y, w, h, cnt = item
                solidity = get_solidity(cnt)
                ar = w / float(h)
                # 如果实心度非常高 (>0.85)，通常是噪点块
                # 除非它是扁平的 (减号)
                if solidity > 0.85:
                    if ar > 1.5: return True # Big Minus
                    return False 
                return True
            
            # 策略 A: 两个数字中间寻找
            if len(digits) >= 2:
                # 假设前两个大轮廓是数字
                d1 = digits[0]
                d2 = digits[1]
                
                d1_center = d1[0] + d1[2]/2
                d2_center = d2[0] + d2[2]/2
                
                # 寻找位于两个数字中心之间的轮廓
                middle_candidates = []
                for item in valid_items:
                    if item == d1 or item == d2: continue
                    
                    ix, iy, iw, ih, icnt = item
                    # 排除过大的干扰物 (如边框)
                    if iw > 60 or ih > 60: continue

                    icenter = ix + iw/2
                    
                    # 宽松的中间判定: 在 d1 右边界和 d2 左边界之间，或者中心在两者中心之间
                    # 修正：扩大搜索范围，允许稍微偏离中心
                    # d1_right = d1[0] + d1[2]
                    # d2_left = d2[0]
                    # if (d1_right - 10 < ix < d2_left + 10) or (d1_center - 10 < icenter < d2_center + 10):
                    #    middle_candidates.append(item)
                    
                    # 更宽松的判定：只要在两个数字的x范围内即可
                    d1_x_end = d1[0] + d1[2]
                    d2_x_start = d2[0]
                    
                    # 情况1: 轮廓在两数字之间
                    # 放宽条件：允许轮廓稍微重叠数字边缘 (防止粘连判定失败)
                    is_between = (ix > d1[0] - 5 and ix < d2_x_start + d2[2] + 5) 
                    
                    # 情况2: 轮廓中心在两数字中心之间
                    is_center_between = (icenter > d1_center - 10 and icenter < d2_center + 10)
                    
                    if is_between or is_center_between:
                         middle_candidates.append(item)
                
                if middle_candidates:
                    # 优先寻找大尺寸的运算符 (/, +)
                    # 按面积降序排序
                    middle_candidates.sort(key=lambda x: x[2]*x[3], reverse=True)
                    
                    # 1. 尝试找 Big Ops (h > 20)
                    big_ops = [c for c in middle_candidates if c[3] > 20]
                    for op in big_ops:
                        if is_valid_op_candidate(op):
                            op_candidate = op
                            break
                    
                    # 2. 如果没有 Big Ops，找其他的
                    if not op_candidate:
                        for op in middle_candidates:
                             if is_valid_op_candidate(op):
                                op_candidate = op
                                break
            
            
            # 策略 B: 全局中间区域搜索 (如果策略 A 失败)
            if not op_candidate:
                center_candidates = []
                center_x_min = img_w * 0.3
                center_x_max = img_w * 0.7
                
                for item in valid_items:
                    # 排除已识别的数字 (如果有)
                    if item in digits: continue
                    
                    x, y, w, h, cnt = item
                    center_x = x + w / 2
                    if center_x_min < center_x < center_x_max:
                         # 排除可能是边框的大物体
                        if w > 50 or h > 60: continue
                        center_candidates.append(item)
                
                if center_candidates:
                     # 同样优先找大尺寸的
                    center_candidates.sort(key=lambda x: x[2]*x[3], reverse=True)
                    
                    for op in center_candidates:
                        if is_valid_op_candidate(op):
                            op_candidate = op
                            break

            if op_candidate:
                x, y, w, h, cnt = op_candidate
                ar = w / float(h)
                
                # 计算实心度 (Solidity) = 轮廓面积 / 凸包面积
                # +号是空的十字，实心度低 (~0.45)
                # *号是实心的，实心度高 (~0.8)
                solidity = get_solidity(cnt)
                
                # 计算 Hu Moments (用于调试和辅助判断)
                moments = cv2.moments(cnt)
                hu = cv2.HuMoments(moments)
                hu_log = -1 * np.sign(hu) * np.log10(np.abs(hu)) if hasattr(hu, '__len__') else []
                hu0 = hu_log[0][0] if len(hu_log) > 0 else 0

                # 1. 模板匹配 (cv2.matchShapes)
                best_match_label = None
                min_score = float('inf')
                
                if self.op_templates:
                    for tmpl in self.op_templates:
                        tmpl_label = tmpl['label']
                        try:
                            # 形状匹配 (越小越相似)
                            score = cv2.matchShapes(cnt, tmpl['contour'], cv2.CONTOURS_MATCH_I1, 0.0)
                            if score < min_score:
                                min_score = score
                                best_match_label = tmpl_label
                        except:
                            pass
                    

                # 2. 几何规则判断 (基于新样本分析) - 优先于弱模板匹配
                
                # Minus (-): 极扁平 (ar > 1.3) 或 高度极小
                # 特殊情况：如果 ar 很大 (如 > 2.5)，几乎肯定是减号
                # 除非...它是被截断的 + 或 / (中间部分)
                if ar > 2.0:
                    # 检查是否是除法斜线的一部分？除法斜线 ar 较小
                    # 检查是否是加号横线？加号横线 ar 较大
                    
                    # 增加一个检查：如果宽度非常大 (> 20) 且高度非常小 (< 10)，极大概率是减号
                    if w > 20 and h < 10:
                        return '-'
                    
                    # 否则，可能是粘连的干扰
                    # 如果 Solidity 非常高，可能是粘连的文字
                    if solidity > 0.8:
                        return None # 让它继续走下面的逻辑或者返回 None
                    return '-'

                if h < 12:
                    return '-'
                
                # 如果高度适中但长宽比很大，也是减号
                if ar > 1.3 and h < 40:
                    return '-'
                
                # Divide (/): 高而瘦 (ar < 0.6)
                if ar < 0.6:
                    return '/'
                
                # Plus (+) vs Multiply (*): 都是方形 (0.7 < ar < 1.4)
                if 0.6 < ar < 1.5:
                    # 结合 Solidity (实心度) 和 像素分布 进行综合判断
                    # 新样本分析: + (Solidity ~0.46), * (Solidity ~0.79)
                    
                    # 1. 如果 Solidity 较高，很可能是 * (实心或粗体)
                    # 降低阈值以适应更细的 * 号 (如 0.6)
                    # 但也不能太高 (如 > 0.82)，否则可能是噪点块
                    if 0.6 < solidity < 0.82:
                        return '*'
                        
                    # 2. 如果 Solidity 较低，可能是 + 也可能是 x (瘦体的 *)
                    # 使用像素网格法区分
                    roi = opened[y:y+h, x:x+w]
                    return self._distinguish_plus_multiply(roi, task_id)

                # 3. 模板匹配兜底 (仅当分数非常高时)
                # 放宽一点点，因为有些字符粘连会导致分数降低
                if best_match_label and min_score < 0.2:
                     return best_match_label


                # 最后的最后，默认返回 + (出现概率较高)
                return '+'
            
            return None

            
        except Exception as e:
            log_error(f"[{task_id}] CV 运算符识别失败: {str(e)}")
            return None

    def solve_arithmetic(self, image_bytes, task_id):
        """
        识别算术验证码并返回计算结果
        """
        if not self.reader and not self.ocr:
            log_error(f"[{task_id}] 验证码识别模块均未就绪")
            return None

        # 1. 首先尝试 CV 识别运算符
        cv_op = self.identify_operator_cv(image_bytes, task_id)
        if cv_op:
            log_info(f"[{task_id}] CV 识别到运算符: {cv_op}")

        candidates = []

        def parse_and_calc(text, forced_op=None):
            if not text: return None, None
            # 清理
            clean = text.lower().replace('x', '*').replace('×', '*').replace('÷', '/')
            clean = clean.replace('=', '').replace('?', '').replace('？', '').replace(' ', '')
            
            # 常见 OCR 错误修正
            clean = clean.replace('t', '+').replace('f', '+').replace('k', '+')
            clean = clean.replace('l', '1').replace('i', '1').replace('o', '0')
            clean = clean.replace('g', '9').replace('z', '2').replace('b', '6')
            clean = clean.replace('s', '5').replace('q', '9')
            
            # 如果有强制运算符，优先使用
            if forced_op:
                # 提取数字
                digits = re.findall(r'\d', clean)
                if len(digits) >= 2:
                    n1 = int(digits[0])
                    n2 = int(digits[1])
                    
                    # 特殊处理：如果运算符是 / 且 n2 是 0 (可能是 / 被误识别为 0)，尝试取第三个数字
                    if forced_op == '/' and n2 == 0 and len(digits) > 2:
                         n2 = int(digits[2])
                    
                    # 特殊处理：如果 n2 为 0 且 op 为 /，则无效
                    if forced_op == '/' and n2 == 0:
                        return None, None
                    
                    # 容错：如果 n2 为 0，但原图是减法，可能是 1-0=1
                    # (不做特殊处理，让它自然计算)

                    # 容错：如果 CV 识别为 -，但 OCR 识别出了 + (例如 7+6=)，且 n2 > n1 (如 7-6=1 vs 7+6=13)
                    # 这通常发生在加号的竖线很淡，CV 漏检，但 OCR 看到了
                    # 或者 CV 识别出了 -，但实际上是 + (竖线断开)
                    
                    if forced_op == '-' and n1 < n2:
                         # 检查原始 OCR 结果是否有 + 号
                         if '+' in clean or 't' in clean or 'f' in clean:
                            #  log_info(f"[{task_id}] CV detected '-' but OCR suggests '+' and n1 < n2 ({n1} < {n2}). Switching to '+'.")
                             forced_op = '+'
                             result = str(n1 + n2)
                             return result, {'n1': n1, 'n2': n2, 'op': '+', 'src': 'ocr_correction'}

                    # 在这里我们优先信任 CV 的运算符，除非计算结果极不合理
                    # 比如 7/1 算出来 0 (因为 n2=1 误识别为 0?) -> 上面已经处理了
                    
                    # 如果是除法，且结果是整数，非常可信
                    if forced_op == '/':
                        if n2 != 0 and n1 % n2 == 0:
                            pass # Keep it
                        elif n2 == 1: # 7/1 = 7
                            pass
                        else:
                            # 除不尽，可能是误判
                            # 尝试回退到减法? 不，相信 CV
                            pass

                    result = None
                    try:
                        if forced_op == '+': result = str(n1 + n2)
                        elif forced_op == '-': result = str(n1 - n2)
                        elif forced_op == '*': result = str(n1 * n2)
                        elif forced_op == '/': result = str(int(n1 / n2))
                        
                        if result:
                            return result, {'n1': n1, 'n2': n2, 'op': forced_op, 'src': 'cv_forced'}
                    except Exception:
                        pass

            # 尝试正则匹配
            match = re.search(r'(\d)\s*([\+\-\*\/])\s*(\d)', clean)
            if match:
                n1 = int(match.group(1))
                op = match.group(2)
                n2 = int(match.group(3))
                result = None
                if op == '+': result = str(n1 + n2)
                elif op == '-': result = str(n1 - n2)
                elif op == '*': result = str(n1 * n2)
                elif op == '/': result = str(int(n1 / n2))
                
                if result:
                    return result, {'n1': n1, 'n2': n2, 'op': op}
            return None, None

        def heuristic_infer(text, forced_op=None):
            """启发式推断"""
            if not text: return None, None
            clean = text.replace('=', '').replace('?', '').replace(' ', '')
            
            digits = re.findall(r'\d', clean)
            
            if len(digits) >= 2:
                n1 = int(digits[0])
                n2 = int(digits[1])
                clean_val = f"{n1}{n2}"

                # 如果有强制运算符
                if forced_op:
                    result = None
                    if forced_op == '+': result = str(n1 + n2)
                    elif forced_op == '-': result = str(n1 - n2)
                    elif forced_op == '*': result = str(n1 * n2)
                    elif forced_op == '/': result = str(int(n1 / n2))
                    if result:
                        log_info(f"[{task_id}] 使用 CV 运算符 ({forced_op}) 进行计算: {n1}{forced_op}{n2}={result}")
                        return result, {'n1': n1, 'n2': n2, 'op': forced_op}

                # ... (原有的启发式逻辑作为 fallback)
                if n1 == n2:
                    log_info(f"[{task_id}] 检测到可能的运算符丢失 (Result: {clean_val}, n1==n2)，优先尝试减法: {n1}-{n2}")
                    return str(n1 - n2), {'n1': n1, 'n2': n2, 'op': '-'}
                
                if n2 == 1:
                    log_info(f"[{task_id}] 检测到可能的运算符丢失 (Result: {clean_val}, n2=1)，优先尝试减法: {n1}-{n2}")
                    return str(n1 - n2), {'n1': n1, 'n2': n2, 'op': '-'}

                if n2 == 0:
                    log_info(f"[{task_id}] 检测到可能的运算符丢失 (Result: {clean_val}, n2=0)，优先尝试乘法: {n1}*0")
                    return "0", {'n1': n1, 'n2': 0, 'op': '*'}

                log_info(f"[{task_id}] 检测到可能的运算符丢失 (Result: {clean_val})，优先尝试乘法: {n1}*{n2}")
                return str(n1 * n2), {'n1': n1, 'n2': n2, 'op': '*'}

            return None, None

        def process_result(raw_text, strategy_name):
            if not raw_text: return
            log_info(f"[{task_id}] 验证码原始识别结果 ({strategy_name}): {raw_text}")
            
            # 1. 常规解析 (带 CV 辅助)
            res, info = parse_and_calc(raw_text, forced_op=cv_op)
            if res:
                log_info(f"[{task_id}] 验证码计算成功 ({strategy_name}): {res}")
                candidates.append({
                    'strategy': strategy_name,
                    'result': res,
                    'raw': raw_text,
                    'info': info,
                    'type': 'parsed'
                })
                return
            
            # 2. 启发式推断 (带 CV 辅助)
            res, info = heuristic_infer(raw_text, forced_op=cv_op)
            if res:
                log_info(f"[{task_id}] 验证码计算成功 ({strategy_name} - Heuristic): {res}")
                candidates.append({
                    'strategy': strategy_name,
                    'result': res,
                    'raw': raw_text,
                    'info': info,
                    'type': 'heuristic'
                })
                return

        # ----------------------
        # Strategy A: EasyOCR
        # ----------------------
        if self.reader:
            try:
                # 限制字符集为数字和运算符
                allow_list = '0123456789+-*/xX=?'

                # 1. EasyOCR - Direct
                results = self.reader.readtext(image_bytes, detail=0, allowlist=allow_list)
                text_easy = "".join(results)
                process_result(text_easy, "EasyOCR")

                # 2. EasyOCR - Enhanced
                enhanced_bytes = self._enhance_image(image_bytes, task_id)
                results_enhanced = self.reader.readtext(enhanced_bytes, detail=0, allowlist=allow_list)
                text_easy_enhanced = "".join(results_enhanced)
                process_result(text_easy_enhanced, "EasyOCR-Enhanced")

                # 3. EasyOCR - Inverted & Dilated (Targeting thin operators like '-')
                try:
                    # 转 numpy -> 解码 -> 转灰度 -> 二值化 -> 反转 -> 膨胀
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if img is not None:
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        # 二值化 (黑底白字)
                        _, binary_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                        # 膨胀 (让白色文字/运算符变粗)
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                        dilated = cv2.dilate(binary_inv, kernel, iterations=1)
                        
                        success, encoded_inv = cv2.imencode('.png', dilated)
                        if success:
                            results_inv = self.reader.readtext(encoded_inv.tobytes(), detail=0, allowlist=allow_list)
                            text_easy_inv = "".join(results_inv)
                            process_result(text_easy_inv, "EasyOCR-Inverted")
                except Exception as e_inv:
                    log_error(f"[{task_id}] EasyOCR-Inverted 预处理失败: {str(e_inv)}")

            except Exception as e:
                log_error(f"[{task_id}] EasyOCR 识别异常: {str(e)}")

        # ----------------------
        # Strategy B: ddddocr
        # ----------------------
        if self.ocr:
            try:
                # 图像增强
                enhanced_bytes = self._enhance_image(image_bytes, task_id)

                # 1. ddddocr - Beta Model
                if hasattr(self, 'ocr_beta') and self.ocr_beta:
                    text_beta = self.ocr_beta.classification(enhanced_bytes)
                    process_result(text_beta, "ddddocr-Beta")

                # 2. ddddocr - Direct (Standard Model)
                text_dd = self.ocr.classification(enhanced_bytes)
                process_result(text_dd, "ddddocr-Standard")

                # 3. ddddocr - Old Model
                if self.ocr_old:
                    text_dd_old = self.ocr_old.classification(enhanced_bytes)
                    process_result(text_dd_old, "ddddocr-Old")
                
                # 4. ddddocr - Raw Image
                text_raw = self.ocr.classification(image_bytes)
                process_result(text_raw, "ddddocr-Raw")

            except Exception as e:
                log_error(f"[{task_id}] ddddocr 识别异常: {str(e)}")

        # ----------------------
        # 结果决策逻辑 (Voting & Priority)
        # ----------------------
        if not candidates:
            log_error(f"[{task_id}] 所有策略均无法解析验证码")
            return None

        log_info(f"[{task_id}] 候选结果: {[c['result'] for c in candidates]}")

        # 1. 投票
        from collections import Counter
        counts = Counter([c['result'] for c in candidates])
        most_common_res, count = counts.most_common(1)[0]
        
        # 如果有压倒性优势 (>= 2 票且超过总数一半，或只有1个结果)
        if count >= 2 or len(candidates) == 1:
            log_info(f"[{task_id}] 采用投票结果: {most_common_res} (Count: {count})")
            return most_common_res

        # 2. 如果票数分散，进行启发式优选
        # 优先选择单位数操作数的算式 (如 9*3) 而非多位数 (如 91-4)
        best_candidate = None
        
        for cand in candidates:
            info = cand.get('info')
            if not info: continue
            
            # 计算分数
            # 基础分
            score = 0
            
            # 策略权重
            if 'Beta' in cand['strategy']: score += 2
            elif 'Standard' in cand['strategy']: score += 1
            
            # 操作数特征
            # 如果操作数都是 < 10 的，极大加分 (通常验证码是 1位 op 1位)
            if info['n1'] < 10 and info['n2'] < 10:
                score += 10
            # 如果操作数 > 20，减分 (除非是加法结果)
            if info['n1'] > 20 or info['n2'] > 20:
                score -= 5
                
            cand['score'] = score
        
        # 按分数排序
        candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
        best = candidates[0]
        log_info(f"[{task_id}] 采用优选结果: {best['result']} (Strategy: {best['strategy']}, Score: {best.get('score')})")
        return best['result']
        log_error(f"[{task_id}] 所有策略均无法解析验证码")      
        return None
