<template>
  <div class="auth-container">
    <!-- 3D背景容器 -->
    <div id="canvas-container"></div>

    <div class="container">
      <!-- 登录/注册卡片 -->
      <div class="auth-card fade-in-up">
        <div class="auth-header">
          <h1 class="auth-title">项目管理平台</h1>
          <p class="auth-subtitle">高效协作，智驭项目</p>
        </div>

        <!-- 登录表单 -->
        <div v-show="activeForm === 'login'" id="login-form">
          <div class="form-group fade-in-up delay-100">
            <label class="form-label" for="login-email">邮箱</label>
            <div class="input-group">
              <el-icon class="input-icon"><Message /></el-icon>
              <el-input
                v-model="loginForm.email"
                type="email"
                id="login-email"
                class="form-input input-with-icon"
                placeholder="请输入您的邮箱"
                :validate-event="true"
                autocomplete="off"
              />
            </div>
            <div class="error-message" v-if="loginErrors.email">{{ loginErrors.email }}</div>
          </div>

          <div class="form-group fade-in-up delay-200">
            <label class="form-label" for="login-password">密码</label>
            <div class="input-group">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="loginForm.password"
                type="password"
                id="login-password"
                class="form-input input-with-icon"
                placeholder="请输入您的密码"
                :validate-event="false"
                :show-password="showLoginPassword"
                autocomplete="new-password"
              />
            </div>
            <div class="error-message" v-if="loginErrors.password">{{ loginErrors.password }}</div>
          </div>

          <div class="form-options fade-in-up delay-300">
            <label class="remember-me">
              <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
            </label>
            <a href="#" class="forgot-password" @click.prevent="switchForm('forgotPassword')">忘记密码？</a>
          </div>

          <el-button
            type="primary"
            class="btn btn-primary fade-in-up delay-400"
            id="login-button"
            @click="handleLogin"
            :loading="isLoading"
          >
            登录
          </el-button>

          <div class="divider fade-in-up delay-400">
            或
          </div>

          <div class="social-login fade-in-up delay-500">
            <el-button class="social-btn" id="feishu-login" @click="handleSocialLogin('飞书')">
              <img src="@/assets/icons/feishu.svg" alt="飞书" class="social-icon" />
              <span class="social-label">飞书</span>
            </el-button>
          </div>

          <div class="switch-form fade-in-up delay-500">
            还没有账号？ <a href="#" @click.prevent="switchForm('register')">立即注册</a>
          </div>
        </div>

        <!-- 注册表单 -->
        <div v-show="activeForm === 'register'" id="register-form">
          <div class="form-group fade-in-up delay-100">
            <label class="form-label" for="register-name">姓名</label>
            <div class="input-group">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="registerForm.name"
                type="text"
                id="register-name"
                class="form-input input-with-icon"
                placeholder="请输入您的姓名"
                :validate-event="false"
                autocomplete="off"
              />
            </div>
            <div class="error-message" v-if="registerErrors.name">{{ registerErrors.name }}</div>
          </div>

          <div class="form-group fade-in-up delay-200">
            <label class="form-label" for="register-email">邮箱</label>
            <div class="input-group">
              <el-icon class="input-icon"><Message /></el-icon>
              <el-input
                v-model="registerForm.email"
                type="email"
                id="register-email"
                class="form-input input-with-icon"
                placeholder="请输入您的邮箱"
                :validate-event="false"
              />
            </div>
            <div class="error-message" v-if="registerErrors.email">{{ registerErrors.email }}</div>
          </div>

          <div class="form-group fade-in-up delay-300">
            <label class="form-label" for="register-password">密码</label>
            <div class="input-group">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="registerForm.password"
                type="password"
                id="register-password"
                class="form-input input-with-icon"
                placeholder="请设置您的密码"
                :validate-event="false"
                :show-password="showRegisterPassword"
              />
            </div>
            <div class="error-message" v-if="registerErrors.password">{{ registerErrors.password }}</div>
          </div>

          <div class="form-group fade-in-up delay-400">
            <label class="form-label" for="register-confirm-password">确认密码</label>
            <div class="input-group">
              <el-icon class="input-icon"><CircleCheck /></el-icon>
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                id="register-confirm-password"
                class="form-input input-with-icon"
                placeholder="请再次输入密码"
                :validate-event="false"
                :show-password="showRegisterConfirmPassword"
                autocomplete="new-password"
              />
            </div>
            <div class="error-message" v-if="registerErrors.confirmPassword">{{ registerErrors.confirmPassword }}</div>
          </div>

          <el-button
            type="primary"
            class="btn btn-primary fade-in-up delay-500"
            id="register-button"
            @click="handleRegister"
            :loading="isLoading"
          >
            注册
          </el-button>

          <div class="switch-form fade-in-up delay-500">
            已有账号？ <a href="#" @click.prevent="switchForm('login')">立即登录</a>
          </div>
        </div>

        <!-- 忘记密码表单 -->
        <div v-show="activeForm === 'forgotPassword'" id="forgot-password-form">
          <div class="form-group fade-in-up delay-100">
            <label class="form-label" for="forgot-email">邮箱</label>
            <div class="input-group">
              <el-icon class="input-icon"><Message /></el-icon>
              <el-input
                v-model="forgotPasswordForm.email"
                type="email"
                id="forgot-email"
                class="form-input input-with-icon"
                placeholder="请输入您的邮箱"
                :validate-event="false"
              />
            </div>
            <div class="error-message" v-if="forgotPasswordErrors.email">{{ forgotPasswordErrors.email }}</div>
          </div>

          <el-button
            type="primary"
            class="btn btn-primary fade-in-up delay-200"
            id="send-reset-link-button"
            @click="handleSendResetLink"
            :loading="isLoading"
          >
            发送重置链接
          </el-button>

          <div class="switch-form fade-in-up delay-300">
            <a href="#" @click.prevent="switchForm('login')">返回登录</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/Auth/user';
import { register } from '@/api/Auth/auth';
import * as THREE from 'three';
import { Message, Lock, User, CircleCheck } from '@element-plus/icons-vue';

export default {
  name: 'AuthView',
  components: {
    Message,
    Lock,
    User,
    CircleCheck
  },
  setup() {
    const router = useRouter();
    const userStore = useUserStore();

    // 响应式数据
    const activeForm = ref('login');
    const isLoading = ref(false);
    const isDesktop = ref(window.innerWidth >= 1024);
    const showLoginPassword = ref(false);
    const showRegisterPassword = ref(false);
    const showRegisterConfirmPassword = ref(false);

    // 表单数据
    const loginForm = reactive({
      email: '',
      password: '',
      rememberMe: false
    });

    const registerForm = reactive({
      name: '',
      email: '',
      password: '',
      confirmPassword: ''
    });

    const forgotPasswordForm = reactive({
      email: ''
    });

    // 错误信息
    const loginErrors = reactive({});
    const registerErrors = reactive({});
    const forgotPasswordErrors = reactive({});

    // 表单切换
    const switchForm = (form) => {
      activeForm.value = form;
      // 清空错误信息
      Object.keys(loginErrors).forEach(key => delete loginErrors[key]);
      Object.keys(registerErrors).forEach(key => delete registerErrors[key]);
      Object.keys(forgotPasswordErrors).forEach(key => delete forgotPasswordErrors[key]);
    };

    // 邮箱格式验证
    const isValidEmail = (email) => {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return re.test(email);
    };

    // 表单验证
    const validateLoginForm = () => {
      let isValid = true;
      Object.keys(loginErrors).forEach(key => delete loginErrors[key]);

      if (!loginForm.email) {
        loginErrors.email = '请输入邮箱';
        isValid = false;
      } else if (!isValidEmail(loginForm.email)) {
        loginErrors.email = '请输入有效的邮箱地址';
        isValid = false;
      }

      if (!loginForm.password) {
        loginErrors.password = '请输入密码';
        isValid = false;
      } else if (loginForm.password.length < 6) {
        loginErrors.password = '密码长度不能少于6位';
        isValid = false;
      }

      return isValid;
    };

    const validateRegisterForm = () => {
      let isValid = true;
      Object.keys(registerErrors).forEach(key => delete registerErrors[key]);

      if (!registerForm.name) {
        registerErrors.name = '请输入姓名';
        isValid = false;
      }

      if (!registerForm.email) {
        registerErrors.email = '请输入邮箱';
        isValid = false;
      } else if (!isValidEmail(registerForm.email)) {
        registerErrors.email = '请输入有效的邮箱地址';
        isValid = false;
      }

      if (!registerForm.password) {
        registerErrors.password = '请设置密码';
        isValid = false;
      } else if (registerForm.password.length < 6) {
        registerErrors.password = '密码长度不能少于6位';
        isValid = false;
      }

      if (!registerForm.confirmPassword) {
        registerErrors.confirmPassword = '请确认密码';
        isValid = false;
      } else if (registerForm.confirmPassword !== registerForm.password) {
        registerErrors.confirmPassword = '两次输入的密码不一致';
        isValid = false;
      }

      return isValid;
    };

    const validateForgotPasswordForm = () => {
      let isValid = true;
      Object.keys(forgotPasswordErrors).forEach(key => delete forgotPasswordErrors[key]);

      if (!forgotPasswordForm.email) {
        forgotPasswordErrors.email = '请输入邮箱';
        isValid = false;
      } else if (!isValidEmail(forgotPasswordErrors.email)) {
        forgotPasswordErrors.email = '请输入有效的邮箱地址';
        isValid = false;
      }

      return isValid;
    };

    // 表单提交处理
    const handleLogin = async () => {
      if (!validateLoginForm()) return;

      isLoading.value = true;
      try {
        await userStore.login({
          email: loginForm.email,
          password: loginForm.password
        });
        
        // 处理记住我逻辑
        if (loginForm.rememberMe) {
          localStorage.setItem('rememberMeData', JSON.stringify({
            email: loginForm.email,
            // 简单Base64编码，避免明文直接存储
            password: window.btoa(loginForm.password) 
          }));
        } else {
          localStorage.removeItem('rememberMeData');
        }

        ElMessage({
          message: '登录成功！',
          type: 'success',
          duration: 2000
        });

        // 使用replace替换当前路由，避免用户回退到登录页
        router.replace('/');
      } catch (error) {
        console.error(error);
      } finally {
        isLoading.value = false;
      }
    };

    const handleRegister = async () => {
      if (!validateRegisterForm()) return;

      isLoading.value = true;
      try {
        await register({
          name: registerForm.name,
          email: registerForm.email,
          password: registerForm.password
        });
        
        ElMessage({
          message: '注册成功！',
          type: 'success',
          duration: 2000
        });

        // 切换到登录表单
        switchForm('login');
      } catch (error) {
        console.error(error);
      } finally {
        isLoading.value = false;
      }
    };

    const handleSendResetLink = async () => {
      if (!validateForgotPasswordForm()) return;

      isLoading.value = true;
      try {
        // 模拟API请求
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // 模拟发送成功
        ElMessage({
          message: '重置链接已发送到您的邮箱！',
          type: 'success',
          duration: 2000
        });

        // 切换到登录表单
        switchForm('login');
      } catch (error) {
        ElMessage.error('发送失败，请稍后重试');
      } finally {
        isLoading.value = false;
      }
    };

    const handleSocialLogin = (platform) => {
      ElMessage({
        message: `${platform} 登录功能正在开发中，敬请期待！`,
        type: 'info',
        duration: 2000
      });
    };

    // 初始化3D背景
    let scene, camera, renderer, particlesMesh;

    const initThreeBackground = () => {
      const container = document.getElementById('canvas-container');
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);

      // 创建粒子系统
      const particlesGeometry = new THREE.BufferGeometry();
      const particlesCount = 1500;
      
      const posArray = new Float32Array(particlesCount * 3);
      const colorsArray = new Float32Array(particlesCount * 3);
      
      const colors = [
        [0.2, 0.5, 0.8], // 蓝色
        [0.8, 0.2, 0.5], // 粉色
        [0.2, 0.8, 0.5], // 绿色
        [0.8, 0.5, 0.2]  // 橙色
      ];
      
      for (let i = 0; i < particlesCount * 3; i++) {
        // 位置
        posArray[i] = (Math.random() - 0.5) * 10;
        
        // 颜色
        const colorIndex = Math.floor(Math.random() * colors.length);
        colorsArray[i * 3] = colors[colorIndex][0];
        colorsArray[i * 3 + 1] = colors[colorIndex][1];
        colorsArray[i * 3 + 2] = colors[colorIndex][2];
      }
      
      particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
      particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colorsArray, 3));
      
      const particlesMaterial = new THREE.PointsMaterial({
        size: 0.02,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
      });
      
      particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
      scene.add(particlesMesh);

      camera.position.z = 5;

      // 动画循环
      const animate = () => {
        requestAnimationFrame(animate);
        
        particlesMesh.rotation.x += 0.0005;
        particlesMesh.rotation.y += 0.0005;
        
        renderer.render(scene, camera);
      };

      animate();
    };

    // 响应窗口大小变化
    const handleResize = () => {
      isDesktop.value = window.innerWidth >= 1024;
      
      if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      }
    };

    // 生命周期钩子
    // 初始化加载记住的账号密码
    onMounted(() => {
      initThreeBackground();
      window.addEventListener('resize', handleResize);
      
      const rememberMeData = localStorage.getItem('rememberMeData');
      if (rememberMeData) {
        try {
          const data = JSON.parse(rememberMeData);
          loginForm.email = data.email;
          // 简单Base64解码，避免明文直接显示在LocalStorage
          loginForm.password = window.atob(data.password); 
          loginForm.rememberMe = true;
        } catch (e) {
          console.error('Failed to parse rememberMe data', e);
          localStorage.removeItem('rememberMeData');
        }
      }
    });

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize);
      if (renderer) {
        renderer.dispose();
      }
      if (particlesMesh) {
        particlesMesh.geometry.dispose();
        particlesMesh.material.dispose();
      }
    });

    return {
      activeForm,
      isLoading,
      isDesktop,
      showLoginPassword,
      showRegisterPassword,
      showRegisterConfirmPassword,
      loginForm,
      registerForm,
      forgotPasswordForm,
      loginErrors,
      registerErrors,
      forgotPasswordErrors,
      switchForm,
      handleLogin,
      handleRegister,
      handleSendResetLink,
      handleSocialLogin
    };
  }
};
</script>
