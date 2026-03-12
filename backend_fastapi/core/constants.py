# 状态到进度的映射
# 保持与前端 src/utils/constants.js 中 REQUIREMENT_STATUS_PROGRESS_MAP 一致
REQUIREMENT_STATUS_PROGRESS_MAP = {
    'draft': 0,
    'pending': 10,
    'reviewing': 20,
    'tech_review': 30,
    'planning': 40,
    'developing': 60,
    'testing': 60,
    'completed': 100,
    'closed': 100,
    'suspended': 0,
    'accepting': 90,
    'online': 100,
    'not_started': 0,
    'in_progress': 50
}

# 缺陷状态到进度的映射
DEFECT_STATUS_PROGRESS_MAP = {
    'New': 0,
    'In_Progress': 20,
    'Resolved': 50,
    'Verified': 90,
    'Closed': 100,
    'Rejected': 100,
    'Reopened': 0
}
