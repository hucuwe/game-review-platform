<template>
  <div class="about">
    <div class="about-header">
      <h1>关于我们</h1>
      <p>专业的游戏评论与评分平台</p>
    </div>

    <div class="content-wrapper">
      <el-row :gutter="24">
        <el-col :span="24">
          <el-card shadow="hover" class="intro-card">
            <h2>平台简介</h2>
            <p>游戏评论平台是一个专注于为玩家提供专业游戏评分和评论服务的社区平台。我们致力于帮助玩家发现优质游戏，分享游戏体验，建立活跃的游戏社区。</p>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="24" style="margin-top: 24px">
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon :size="48" color="#409eff"><Star /></el-icon>
            </div>
            <h3>多维度评分</h3>
            <p>从玩法、画面、剧情、音效等多个维度对游戏进行全面评价</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon :size="48" color="#67c23a"><ChatDotRound /></el-icon>
            </div>
            <h3>互动评论</h3>
            <p>发表评论、回复讨论、点赞互动，与其他玩家分享游戏心得</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="feature-card">
            <div class="feature-icon">
              <el-icon :size="48" color="#e6a23c"><TrendCharts /></el-icon>
            </div>
            <h3>热门推荐</h3>
            <p>基于评分和热度的智能推荐，帮你发现最值得玩的游戏</p>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="24" style="margin-top: 24px">
        <el-col :span="12">
          <el-card shadow="hover">
            <h2>联系我们</h2>
            <div class="contact-info">
              <p><el-icon><Message /></el-icon> 邮箱：contact@example.com</p>
              <p><el-icon><Phone /></el-icon> 电话：123-456-7890</p>
              <p><el-icon><Location /></el-icon> 地址：某某市某某区某某路123号</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <h2>技术栈</h2>
            <div class="tech-stack">
              <el-tag>Vue 3</el-tag>
              <el-tag type="success">Element Plus</el-tag>
              <el-tag type="warning">Flask</el-tag>
              <el-tag type="danger">MySQL</el-tag>
              <el-tag type="info">Python</el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.about {
  background-color: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.about-header {
  background: linear-gradient(135deg,#7117ea,#ea6060);
  color: white;
  padding: 60px 20px;
  text-align: center;
}

.about-header h1 {
  font-size: 42px;
  margin-bottom: 15px;
}

.about-header p {
  font-size: 18px;
  opacity: 0.9;
}

.content-wrapper {
  max-width: 1200px;
  margin: -40px auto 0;
  padding: 0 20px 40px;
}

.intro-card h2 {
  color: #303133;
  margin-bottom: 20px;
}

.intro-card p {
  color: #606266;
  line-height: 1.8;
  font-size: 16px;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
}

.feature-icon {
  margin-bottom: 20px;
}

.feature-card h3 {
  color: #303133;
  margin-bottom: 15px;
  font-size: 20px;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
}

.contact-info p {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
  color: #606266;
  font-size: 15px;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tech-stack .el-tag {
  font-size: 14px;
  padding: 8px 16px;
}
</style>
