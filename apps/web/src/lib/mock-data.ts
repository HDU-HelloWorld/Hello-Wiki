export const dashboardStats = [
  {
    label: "Wiki 页面",
    value: "128",
    hint: "较昨日 +12",
    tone: "blue" as const,
  },
  {
    label: "今日对话",
    value: "342",
    hint: "客服高峰 14:00",
    tone: "green" as const,
  },
  {
    label: "知识覆盖率",
    value: "87%",
    hint: "按已回答问题计算",
    tone: "amber" as const,
  },
  {
    label: "待审核",
    value: "9",
    hint: "含 3 条冲突变更",
    tone: "red" as const,
  },
];

export const documents = [
  {
    id: "doc-1001",
    name: "2026 本科招生政策.pdf",
    status: "compiled",
    statusLabel: "已编译",
    wikiPages: 18,
    owner: "招生办",
    uploadedAt: "今天 09:20",
  },
  {
    id: "doc-1002",
    name: "奖学金评定办法.docx",
    status: "compiling",
    statusLabel: "编译中",
    wikiPages: 6,
    owner: "学生处",
    uploadedAt: "今天 10:12",
  },
  {
    id: "doc-1003",
    name: "宿舍管理问答.md",
    status: "pending",
    statusLabel: "待编译",
    wikiPages: 0,
    owner: "后勤中心",
    uploadedAt: "昨天 18:04",
  },
  {
    id: "doc-1004",
    name: "转专业实施细则.pdf",
    status: "failed",
    statusLabel: "失败",
    wikiPages: 0,
    owner: "教务处",
    uploadedAt: "昨天 16:35",
  },
];

export const conversations = [
  {
    id: "conv-1",
    question: "外省考生可以申请转专业吗？",
    status: "answered",
    statusLabel: "已回答",
    time: "2 分钟前",
  },
  {
    id: "conv-2",
    question: "港澳台学生奖学金是否单独评定？",
    status: "unknown",
    statusLabel: "未知",
    time: "12 分钟前",
  },
  {
    id: "conv-3",
    question: "综合评价招生需要准备哪些材料？",
    status: "answered",
    statusLabel: "已回答",
    time: "28 分钟前",
  },
];

export const wikiPages = [
  {
    id: 1,
    title: "招生政策总览",
    category: "招生政策",
    tags: ["招生", "本科", "政策"],
    updatedAt: "2026-05-24 16:30",
    source: "2026 本科招生政策.pdf",
    summary: "汇总本科招生批次、录取原则、咨询渠道和注意事项。",
    content:
      "本科招生采用统一考试录取与综合评价相结合的方式。考生应关注各省招生计划、专业限制与志愿填报时间。相关政策变更以学校招生网最新公告为准。",
  },
  {
    id: 2,
    title: "奖学金政策",
    category: "学生资助",
    tags: ["奖学金", "资助", "评定"],
    updatedAt: "2026-05-23 11:05",
    source: "奖学金评定办法.docx",
    summary: "说明国家奖学金、校级奖学金和专项奖学金的评定条件。",
    content:
      "奖学金评定综合考虑学业成绩、综合素质和诚信记录。国家奖学金通常面向二年级及以上学生，校级奖学金按学院推荐、学校审核流程执行。",
  },
  {
    id: 3,
    title: "宿舍管理常见问题",
    category: "校园服务",
    tags: ["宿舍", "后勤", "生活"],
    updatedAt: "2026-05-22 09:44",
    source: "宿舍管理问答.md",
    summary: "覆盖住宿申请、调宿、维修和假期留宿流程。",
    content:
      "新生住宿由学校统一分配。学生如需调宿，应先向学院提交申请，经后勤中心审核后办理。宿舍维修可通过后勤服务平台提交工单。",
  },
];

export const compileJobs = [
  { id: "job-1", name: "奖学金评定办法.docx", progress: 68, status: "running" },
  { id: "job-2", name: "宿舍管理问答.md", progress: 0, status: "waiting" },
  { id: "job-3", name: "转专业实施细则.pdf", progress: 0, status: "failed" },
];

export const compileSteps = [
  "文档解析",
  "文本分块",
  "概念提取",
  "冲突检测",
  "Wiki 生成",
  "链接构建",
  "入库与审核",
];

export const compileLogs = [
  "[INFO] 收到任务 job-1，开始解析奖学金评定办法.docx",
  "[SUCCESS] 文本分块完成，共 42 个语义段落",
  "[INFO] 正在提取核心概念：国家奖学金、校级奖学金、困难补助",
  "[WARN] 检测到与旧版页面存在评定时间差异，已加入审核队列",
];

export const auditItems = [
  {
    id: "audit-1",
    title: "奖学金政策",
    type: "conflict",
    owner: "知识编辑",
    time: "10 分钟前",
  },
  {
    id: "audit-2",
    title: "综合评价材料清单",
    type: "pending",
    owner: "招生办",
    time: "32 分钟前",
  },
  {
    id: "audit-3",
    title: "宿舍调换流程",
    type: "pending",
    owner: "后勤中心",
    time: "1 小时前",
  },
];

export const dialogLogs = [
  {
    id: "d-1",
    user: "访客 0812",
    question: "奖学金什么时候申请？",
    result: "已回答",
    score: "👍",
  },
  {
    id: "d-2",
    user: "访客 0921",
    question: "港澳台学生是否适用？",
    result: "未知",
    score: "待补充",
  },
  {
    id: "d-3",
    user: "客服坐席 A",
    question: "转专业有什么限制？",
    result: "已回答",
    score: "👍",
  },
];

export const unresolvedQuestions = [
  { question: "港澳台学生奖学金是否单独评定？", count: 18, owner: "学生处" },
  { question: "艺术类专业是否允许转专业？", count: 11, owner: "教务处" },
  { question: "国际学生宿舍费用如何计算？", count: 7, owner: "国际学院" },
];

export const simulationResults = [
  {
    id: "s-1",
    scenario: "招生咨询高频问题",
    accuracy: "91%",
    coverage: "86%",
    consistency: "93%",
  },
  {
    id: "s-2",
    scenario: "奖助学金问答",
    accuracy: "84%",
    coverage: "79%",
    consistency: "88%",
  },
  {
    id: "s-3",
    scenario: "校园生活服务",
    accuracy: "89%",
    coverage: "82%",
    consistency: "90%",
  },
];

export const channelCards = [
  {
    title: "网站 JS SDK",
    status: "online",
    detail: "官网浮窗，支持复制嵌入代码",
  },
  {
    title: "微信公众号",
    status: "pending",
    detail: "Token 与 EncodingAESKey 待配置",
  },
  {
    title: "REST API",
    status: "online",
    detail: "3 个活跃 API Key，本月 12,480 次调用",
  },
];

export const members = [
  {
    id: "u-1",
    name: "管理员",
    role: "超级管理员",
    team: "默认空间",
    status: "online",
  },
  {
    id: "u-2",
    name: "知识编辑",
    role: "编辑",
    team: "招生知识库",
    status: "online",
  },
  {
    id: "u-3",
    name: "客服坐席",
    role: "只读",
    team: "客服中心",
    status: "offline",
  },
];

export const serviceStatuses = [
  { name: "FastAPI Backend", status: "online", usage: "24%" },
  { name: "Compile Worker", status: "online", usage: "48%" },
  { name: "Agent Gateway", status: "online", usage: "31%" },
  { name: "Vector Store", status: "online", usage: "57%" },
];
