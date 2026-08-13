#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DAILY_DIR = DATA_DIR / "daily"
VERIFIED_SOURCE_PATH = DATA_DIR / "verified_jobs.json"
FIELDS = [
    "日期",
    "平台",
    "岗位名称",
    "公司名称",
    "公司类型",
    "城市",
    "薪资范围",
    "经验要求",
    "学历要求",
    "岗位链接",
    "公司工商验证",
    "招聘信息验证",
    "备注",
    "是否新增",
]

CURATED_ADDITIONS = [
    {
        "平台": "公司官网招聘页",
        "岗位名称": "高级运营设计师-活动运营设计（J97076）",
        "公司名称": "百度（Baidu）",
        "公司类型": "稳定民企（纳斯达克/港股上市、10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3-5年或5年以上",
        "学历要求": "未披露",
        "岗位链接": "https://talent.baidu.com/jobs/detail/SOCIAL/f66154f6-df92-40c8-b18f-959029a14aeb",
        "公司工商验证": "百度投资者关系官网可核验公司在纳斯达克及香港联交所上市，并持续披露2026年财报与监管文件；百度为员工规模超过万人的稳定上市科技企业。",
        "招聘信息验证": "2026-08-13 百度官方招聘详情页可直接访问并显示“申请职位”，岗位为PSIG北京高级运营设计师、招聘1人、发布日期2026-05-18；职责覆盖百度文库和网盘大型活动、品牌IP、AIGC及3D设计。",
        "备注": "与4.5年经验高度匹配，但属于运营视觉边界岗位而非纯产品UI/UX；适合有大型线上活动、品牌IP、字体排版、3D或AIGC案例者。作品集需随简历提交，投递需登录百度招聘账号。",
    },
    {
        "平台": "公司官网招聘页",
        "岗位名称": "UI设计师（J103371）",
        "公司名称": "百度（Baidu）",
        "公司类型": "稳定民企（纳斯达克/港股上市、10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "1年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://talent.baidu.com/jobs/detail/SOCIAL/8972f75c-6815-4cfe-8793-ad3650c9fac9",
        "公司工商验证": "百度投资者关系官网确认公司在纳斯达克（BIDU）及香港联交所（9888）上市，总部位于北京；官网披露截至2025年末约有33500名全职员工，符合上市且万人以上稳定民企门槛。",
        "招聘信息验证": "2026-08-12 百度官方招聘详情页可直接访问（HTTP 200），显示PSIG北京UI设计师岗位、招聘1人、发布日期2026-07-21；职责覆盖百度网盘与文库的AI应用、产品营销、商业付费和互动玩法设计，页面提供登录入口。",
        "备注": "明示门槛为1年以上，低于候选人的4.5年经验，但复杂链路、体系化UI、商业转化与AIGC工作流具有较高匹配度；建议投递前确认职级和薪资带宽，作品集突出复杂产品链路、增长设计及Figma/AE/AIGC实践。投递需登录百度招聘账号。",
    },
    {
        "平台": "公司官网招聘页",
        "岗位名称": "高级UI设计师（J99117）",
        "公司名称": "百度（Baidu）",
        "公司类型": "稳定民企（纳斯达克/港股上市、10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "未披露（高级岗位）",
        "学历要求": "本科及以上",
        "岗位链接": "https://talent.baidu.com/jobs/detail/SOCIAL/8499e0ab-b8d6-42cf-a316-8e824382740f",
        "公司工商验证": "百度投资者关系官网确认公司在纳斯达克及香港联交所上市，总部位于北京；官网披露员工规模超过万人，符合稳定上市万人企业门槛。",
        "招聘信息验证": "2026-08-11 百度官方招聘详情页可直接访问，显示PSIG北京高级UI设计师岗位、招聘1人、发布日期2026-07-21；职责覆盖AI产品界面、创新交互、设计系统、动效与复杂项目统筹，页面提供登录入口。",
        "备注": "与J96638同属PSIG但职责更强调主导设计体系与复杂项目管理，适合作为4.5年经验的冲刺岗位；作品集应突出AI产品、设计系统、跨团队推进与Figma/AE动效。投递需登录百度招聘账号。",
    },
    {
        "平台": "公司官网招聘页",
        "岗位名称": "视觉设计师（J11393）",
        "公司名称": "小度科技（百度）",
        "公司类型": "稳定民企（百度旗下/纳斯达克及港股上市体系、10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "2年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://talent.baidu.com/jobs/detail/SOCIAL/7b49bc9c-6516-4ee6-95d1-d7680852a6fa",
        "公司工商验证": "小度科技为百度旗下智能生活与硬件业务品牌；百度投资者关系官网可核验其纳斯达克及香港联交所上市公司体系与万人以上规模。",
        "招聘信息验证": "2026-08-11 百度官方招聘详情页可直接访问，显示小度科技北京视觉设计师岗位、招聘若干、发布日期2026-07-21；要求本科及以上、2年以上互联网经历，页面提供登录入口。",
        "备注": "经验门槛低于4.5年但职责包含产品视觉、设计走查、用户反馈与AI大模型设计实践，匹配度较高；有OS、多端规范、AE/Blender或智能硬件案例者优先。投递需登录百度招聘账号。",
    },
    {
        "平台": "公司官网招聘页",
        "岗位名称": "海外AI赛道——高级用户体验设计师（J97181）",
        "公司名称": "百度（Baidu）",
        "公司类型": "稳定民企（纳斯达克/港股上市、10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://talent.baidu.com/jobs/detail/SOCIAL/37e99a23-6bef-4447-8fd5-54c9e691e54b",
        "公司工商验证": "百度投资者关系官网确认公司在纳斯达克及香港联交所上市，总部位于北京；官网披露员工规模超过万人，符合稳定上市万人企业门槛。",
        "招聘信息验证": "2026-08-11 百度官方招聘详情页可直接访问，显示PSIG北京海外AI赛道高级用户体验设计师岗位、招聘2人、发布日期2026-07-21；要求本科及以上、3年以上视觉设计经验。",
        "备注": "与4.5年经验高度匹配，职责同时覆盖UX调研、UI、动效与海外用户体验；有海外项目、AI产品或韩语/西语能力者优势明显。投递需登录百度招聘账号。",
    },
    {
        "平台": "公司官网招聘页",
        "岗位名称": "高级UI设计师（J96638）",
        "公司名称": "百度（Baidu）",
        "公司类型": "稳定民企（纳斯达克/港股上市、10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "未披露（高级岗位）",
        "学历要求": "本科及以上",
        "岗位链接": "https://talent.baidu.com/jobs/detail/SOCIAL/67d3cc00-f348-453b-be53-704954dedd3c",
        "公司工商验证": "百度投资者关系官网确认公司在纳斯达克（BIDU）及香港联交所（9888）上市，总部位于北京；官网披露截至2025年末约有33500名全职员工，符合上市且万人以上稳定民企门槛。",
        "招聘信息验证": "2026-08-11 百度官方招聘详情页可直接访问，显示PSIG北京高级UI设计师岗位、招聘1人、发布日期2026-07-21；职责聚焦百度AI产品界面、创新交互与视觉表现、设计系统和动效，页面提供登录后投递入口。",
        "备注": "官方渠道新增收录；未明示工作年限，但岗位等级为高级，4.5年且具备AI产品、设计系统、Figma与AE动效案例者值得重点尝试。投递需登录百度招聘账号。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "UI设计师（国有控股）",
        "公司名称": "携汇智联技术（北京）有限公司",
        "公司类型": "国企/国资控股（国资比例超过70%）",
        "城市": "北京",
        "薪资范围": "12-20k/月",
        "经验要求": "3-5年",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CCL1242159910J40898515415.htm",
        "公司工商验证": "智联公开工商信息显示企业成立于2020年、经营状态存续、注册资本3000万元；公司介绍披露国资比例超过70%，股东包括中央企业通用技术集团及多家地方国企、上市公司。国务院国资委公开资料确认通用技术集团为中央直接管理的国有重要骨干企业。",
        "招聘信息验证": "2026-08-10 智联公开职位页可直接访问并显示投递入口，岗位位于北京顺义、12-20k/月、本科、3-5年、全职、招1人；发布者近期活跃，页面显示企业营业信息已审核。",
        "备注": "与4.5年经验高度匹配，职责覆盖用户研究、交互原型、UI视觉、设计文档、可用性测试与持续优化；偏工业互联网和机床互联场景，建议作品集突出复杂B端流程、数据界面和设计规范。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "交互设计师",
        "公司名称": "中国华能集团清洁能源技术研究院有限公司",
        "公司类型": "央企（中国华能集团直属研究机构）",
        "城市": "北京",
        "薪资范围": "15-30k·13薪",
        "经验要求": "3-5年",
        "学历要求": "本科",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC450349620J40870537413.htm",
        "公司工商验证": "智联公开工商信息显示企业为国有控股、经营状态存续、注册资本13.38亿元；公司介绍确认其为中国华能集团直属清洁能源技术研发机构，属于央企体系。",
        "招聘信息验证": "2026-08-07 智联公开职位页仍显示沟通与投递入口，岗位位于北京昌平、15-30k·13薪、本科、3-5年、全职；职责覆盖信息架构、交互原型、UI视觉、设计系统、用户研究和数据迭代。",
        "备注": "与4.5年经验高度匹配，央企稳定性和薪资都较突出，建议今日优先投递；工作涉及Web/移动端能源数字化产品，并需根据项目进程短期出差雄安。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "UX 设计师（AI 产品方向）",
        "公司名称": "软通动力信息技术（集团）股份有限公司",
        "公司类型": "稳定民企（A股上市/10000人+）",
        "城市": "北京",
        "薪资范围": "12-14k/月",
        "经验要求": "3-5年",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC000544460J40809697116.htm",
        "公司工商验证": "软通动力为深交所上市公司（301236）；智联企业页显示营业执照已审核、经营状态存续、员工约90000人，符合上市且万人以上稳定民企门槛。",
        "招聘信息验证": "2026-08-07 智联公开职位页仍有立即沟通和投递入口，岗位位于北京昌平中国移动国际信息港、12-14k/月、3-5年、本科；职责为AI产品多端全链路UX/UI、设计系统与体验优化。",
        "备注": "年限匹配，适合有PC、App、小程序跨端经验及AI产品案例者；岗位明确要求MasterGo、PS/AI、AE和基础3D能力，投递前应确认具体客户、是否驻场及项目周期。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "UI设计师(J11152)",
        "公司名称": "南威软件股份有限公司",
        "公司类型": "稳定民企（A股上市/1000人+）",
        "城市": "北京",
        "薪资范围": "20-30k/月",
        "经验要求": "3-5年",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC455611610J40853888711.htm",
        "公司工商验证": "南威软件为上交所主板上市公司（603636）；公开企业与招聘信息显示公司经营状态存续、规模1000-9999人，符合上市稳定民企门槛。",
        "招聘信息验证": "2026-08-07 智联公开职位详情仍可访问并进入投递流程，岗位位于北京丰台、20-30k/月、本科、3-5年；职责聚焦AI医疗健康产品的用户研究、交互框架、可用性测试和UE规范。",
        "备注": "薪资和年限与4.5年候选人高度匹配，虽然标题为UI，正文更偏全链路UE/UX；有医疗健康、AI、大模型或复杂业务流程案例者建议优先。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "视觉设计",
        "公司名称": "江苏泽宇智能电力股份有限公司",
        "公司类型": "稳定民企（A股上市/1000人+）",
        "城市": "南京",
        "薪资范围": "8-9k/月",
        "经验要求": "1-3年（正文要求2年以上）",
        "学历要求": "大专及以上",
        "岗位链接": "https://m.zhaopin.com/jobs/CC444470320J40770813906.htm",
        "公司工商验证": "深交所及公司公开披露文件确认江苏泽宇智能电力股份有限公司为创业板上市公司，证券简称泽宇智能、股票代码301179；智联企业页标注上市公司、1000-9999人。",
        "招聘信息验证": "2026-08-07 智联南京视觉设计搜索页仍列出该岗位并提供投递入口；职位详情显示南京鼓楼、8-9k/月、招1人，负责软件产品视觉风格、界面设计、用户体验优化和开发落地。",
        "备注": "企业稳定性较好，但薪资与明示年限低于4.5年候选人的常规目标，可作为南京保底岗位；工作地点显示在江苏电力信息技术有限公司，投递前需确认劳动合同主体及是否驻场。",
    },
    {
        "平台": "LinkedIn",
        "岗位名称": "Product Designer (UI/UX)",
        "公司名称": "BJAK",
        "公司类型": "外企（马来西亚知名保险科技品牌）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3年以上",
        "学历要求": "未披露",
        "岗位链接": "https://cn.linkedin.com/jobs/view/product-designer-ui-ux-china-at-bjak-4443776265",
        "公司工商验证": "BJAK 官网披露运营主体为马来西亚注册公司 BJAK Sdn. Bhd.（注册号 201901030483），获马来西亚国家银行批准；官网称其为东南亚大型线上保险平台，服务 600 万以上用户。",
        "招聘信息验证": "2026-08-06 LinkedIn 公共职位页仍显示申请入口，职位地点标注北京、全职、中高级；岗位实际为远程但要求候选人常驻中国，要求 3 年以上数字产品设计经验，完整申请需登录。",
        "备注": "与4.5年经验高度匹配，负责保险、支付、理赔与投资产品的端到端体验、设计系统及移动/Web一致性；英语为主要工作语言，节奏偏快速创业团队，需确认中国境内劳动合同主体、社保公积金和远程办公安排。",
    },
    {
        "平台": "前程无忧",
        "岗位名称": "车载语音助手IP形象设计师",
        "公司名称": "奇瑞控股集团",
        "公司类型": "国企（芜湖国资控股汽车集团）",
        "城市": "芜湖",
        "薪资范围": "10-15k·13薪",
        "经验要求": "3年以上",
        "学历要求": "本科",
        "岗位链接": "https://mshejishi.51job.com/wuhu/jiaohusj/",
        "公司工商验证": "奇瑞控股集团由芜湖市国资体系实际控制，核心整车业务规模大；前程无忧公开职位聚合页将招聘主体标注为国企奇瑞控股集团。",
        "招聘信息验证": "2026-08-06 前程无忧芜湖交互设计公开岗位页仍列出该职位，显示芜湖弋江区、10-15k·13薪、本科、3年以上，并有招聘负责人信息；详情页受平台访问限制，需登录或在列表中继续投递。",
        "备注": "年限与4.5年匹配，偏智能座舱语音助手的IP角色与视觉形象，不是纯产品UI岗；适合有角色设定、品牌IP、动效/3D或车载语音场景作品者，投递前确认职责中界面与交互设计占比。",
    },
    {
        "平台": "LinkedIn",
        "岗位名称": "品牌视觉设计师（AI业务）",
        "公司名称": "美团",
        "公司类型": "稳定民企（港股上市/10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3-5年以上",
        "学历要求": "未披露",
        "岗位链接": "https://cn.linkedin.com/jobs/view/%E5%93%81%E7%89%8C%E8%A7%86%E8%A7%89%E8%AE%BE%E8%AE%A1%E5%B8%88%EF%BC%88ai%E4%B8%9A%E5%8A%A1%EF%BC%89-at-%E7%BE%8E%E5%9B%A2-4443132059",
        "公司工商验证": "美团为香港联交所上市公司（03690.HK），员工规模万人以上；境内招聘及业务运营主体可由上市公司公告和公开企业信息交叉核验。",
        "招聘信息验证": "2026-08-06 LinkedIn 公共职位页仍显示申请入口，岗位位于北京，发布约18小时前；要求3-5年以上品牌或视觉设计经验，职责包括AI业务品牌视觉体系、动效与插画风格、设计规范和组件库建设，完整投递通常需登录。",
        "备注": "经验与4.5年高度匹配，适合有完整品牌视觉系统、AI产品、动效或跨模态设计案例的候选人；作品集应突出从视觉语言定义到多触点落地的全过程。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "外卖用户端-UX设计师",
        "公司名称": "北京三快在线科技有限公司（美团）",
        "公司类型": "稳定民企（港股上市/10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3年以上",
        "学历要求": "本科",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC383625320J40739603809.htm",
        "公司工商验证": "智联公开企业信息显示北京三快在线科技有限公司经营状态存续、营业执照已审核；该公司为美团关联运营主体，美团为香港联交所上市公司（03690.HK），员工规模万人以上。",
        "招聘信息验证": "2026-08-06 智联公开职位页仍显示立即投递入口，岗位位于北京望京美团总部、全职、本科；要求3年以上互联网体验设计经验，负责美团外卖用户端界面、新功能方案、设计规范及上线质量跟进。",
        "备注": "4.5年经验匹配，适合移动端C端、电商或本地生活产品背景；作品集应突出高流量复杂场景、视觉与体验权衡，以及上线后的验证和迭代。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "高级UI/UX设计师",
        "公司名称": "首都文化科技集团有限公司",
        "公司类型": "国企（北京市属一级国企）",
        "城市": "北京",
        "薪资范围": "20-25k/月",
        "经验要求": "5年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CCL1468963210J40908990803.htm",
        "公司工商验证": "北京市国资委监管企业页面确认首都文化科技集团于2023年经北京市委市政府批准成立，为北京市属一级国企；智联营业执照信息显示企业类型为国有独资、经营状态存续。",
        "招聘信息验证": "2026-08-05 智联公开职位页显示立即投递入口，岗位位于北京西城、20-25k/月、本科、5年以上；用人单位为集团旗下京彩游（北京）文化科技有限公司，职责覆盖数字文旅平台小程序、App与官网的全终端UI/UX。",
        "备注": "与4.5年经验只差半年，适合作为国企冲刺岗位；有OTA、本地生活、数字文旅、国风视觉或从0到1设计体系经验时优先。投递前确认劳动合同主体及集团内用工关系。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "视觉设计师(J10042)",
        "公司名称": "北京航天世景信息技术有限公司",
        "公司类型": "央企体系（中国航天科技集团子公司）",
        "城市": "北京",
        "薪资范围": "10-18k/月",
        "经验要求": "5-10年",
        "学历要求": "本科",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC456866220J40945216402.htm",
        "公司工商验证": "航天世景官网确认公司为中国航天科技集团旗下中国四维测绘技术有限公司的全资专业子公司；智联企业页同时标注国有企业、央企子公司，营业执照已审核。",
        "招聘信息验证": "2026-08-05 智联公司招聘页显示该岗位仍在11个在招职位中，可立即投递；地点北京、10-18k/月、本科、5-10年，标签包含界面设计、交互设计、网页端、PS与Sketch。",
        "备注": "央企遥感与时空信息业务，方向兼具产品界面和视觉传播；年限略高于4.5年，可凭B端、数据可视化、GIS/遥感或复杂信息产品经验冲刺。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "海外游戏UI设计师(J11159)",
        "公司名称": "南威软件股份有限公司",
        "公司类型": "稳定民企（A股上市/1000人+）",
        "城市": "北京",
        "薪资范围": "10-15k/月",
        "经验要求": "3年以上",
        "学历要求": "本科",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC455611610J40857949511.htm",
        "公司工商验证": "智联营业执照信息显示南威软件为存续的上市股份有限公司；公司为上交所主板上市企业（603636），企业页标注已上市、1000-9999人。",
        "招聘信息验证": "2026-08-05 智联公开职位页仍有立即投递入口，显示北京丰台、10-15k/月、3-5年、本科；职责为海外休闲游戏整体UI风格、界面、Logo、图标与道具系统设计。",
        "备注": "经验与4.5年匹配，但明显偏游戏美术；有欧美休闲游戏、二合玩法、图标绘制或完整游戏UI案例者优先。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "UX 交互设计师",
        "公司名称": "软通动力信息技术（集团）股份有限公司",
        "公司类型": "稳定民企（A股上市/10000人+）",
        "城市": "南京",
        "薪资范围": "8-12k/月",
        "经验要求": "2年以上",
        "学历要求": "统招本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC000544460J40831269016.htm",
        "公司工商验证": "软通动力为深交所上市公司（301236）；智联企业页标注已上市、10000人以上，并披露员工规模约90000人、营业执照经营状态存续。",
        "招聘信息验证": "2026-08-05 智联公开职位页仍显示立即投递入口，岗位位于南京江宁、8-12k/月、本科；要求2年以上交互设计经验，负责B端需求梳理、用户调研、原型、可用性测试与开发落地。",
        "备注": "年限与4.5年匹配且B端全流程职责清晰；建议确认具体客户、是否驻场、项目周期及加班强度。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "UI设计师",
        "公司名称": "合肥众智软件有限公司",
        "公司类型": "稳定民企（新三板挂牌企业全资子公司）",
        "城市": "合肥",
        "薪资范围": "6-8k/月",
        "经验要求": "3年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC388049220J40854957801.htm",
        "公司工商验证": "公开披露文件确认母公司众智软件科技股份有限公司为全国股转系统挂牌企业（证券代码831185）；其2025年年报列示合肥众智软件有限公司，智联营业执照信息显示该公司为法人独资、经营状态存续。",
        "招聘信息验证": "2026-08-05 智联公开职位页仍显示投递入口，岗位位于合肥蜀山、6-8k/月、3-5年、本科；职责覆盖Web/移动端UI、设计规范、交互优化、AE动效及开发落地。",
        "备注": "经验与4.5年高度匹配，偏城市规划、GIS/BIM等B端信息化产品，稳定性尚可但薪资偏低；适合优先考虑地点与工作节奏者。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "UI设计师",
        "公司名称": "苏州安硕数科数据技术有限公司",
        "公司类型": "稳定民企（A股上市公司控股子公司）",
        "城市": "合肥",
        "薪资范围": "15-17k/月",
        "经验要求": "5年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC703527320J40831916107.htm",
        "公司工商验证": "安硕信息2025年年报披露苏州安硕数科数据技术有限公司为其持股51%的控股子公司；安硕信息为深交所创业板上市公司（300380）。",
        "招聘信息验证": "2026-08-05 智联公开职位页仍可进入投递流程，显示合肥包河、15-17k/月、本科；正文要求5年以上UI设计及2年以上团队管理，负责App、Web交互、设计规范和体验迭代。",
        "备注": "职位卡片显示1-3年但正文明确5年以上，信息存在矛盾；4.5年可冲刺，投递前应向HR确认实际年限门槛、管理职责及是否在中国信达项目现场驻场。",
    },
    {
        "平台": "LinkedIn",
        "岗位名称": "UI Designer",
        "公司名称": "美图公司（Meitu Inc.）",
        "公司类型": "稳定民企（港股上市）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "2年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://cn.linkedin.com/jobs/view/ui-designer-at-meitu-inc-4342698269",
        "公司工商验证": "美图公司官方投资者关系与公司介绍页面披露其于2016年在香港联交所上市，股票代码1357；属于公开披露持续、品牌知名度较高的上市科技企业。",
        "招聘信息验证": "2026-08-03 LinkedIn公开职位页仍显示申请入口，地点北京、全职、中高级；要求本科及以上、2年以上App设计经验，职责覆盖海外产品UX/UI、品牌视觉、动效与设计规范建设，完整申请通常需登录。",
        "备注": "年限与4.5年经验匹配，海外业务、图像/视频类App、动效或品牌设计经验是明显加分项；英文沟通要求较高。",
    },
    {
        "平台": "猎聘",
        "岗位名称": "HCI人机交互设计师-PICO",
        "公司名称": "字节跳动",
        "公司类型": "稳定民企（未上市/10000人+）",
        "城市": "北京",
        "薪资范围": "30-60k·15薪",
        "经验要求": "3年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.liepin.com/job/1977899431.shtml",
        "公司工商验证": "字节跳动为北京核心互联网企业，公开招聘页披露员工规模10000人以上；PICO为其旗下XR品牌。",
        "招聘信息验证": "2026-08-03 猎聘公开职位页仍显示投递入口，招聘方为已认证的字节跳动招聘专家；岗位位于北京海淀、招1人，要求3年以上人机交互经验并提供作品集，完整沟通通常需登录。",
        "备注": "与4.5年经验匹配，重点考察XR、多模态交互、GUI/VUI、传感器与原型落地；有Unity或XR独立开发经验者优先。",
    },
    {
        "平台": "猎聘",
        "岗位名称": "自动驾驶C端交互设计师（萝卜快跑）",
        "公司名称": "百度（Baidu）",
        "公司类型": "稳定民企（纳斯达克/港股上市、10000人+）",
        "城市": "北京",
        "薪资范围": "20-35k·16薪",
        "经验要求": "3年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.liepin.com/job/1975108997.shtml",
        "公司工商验证": "百度官方投资者关系页面披露公司在纳斯达克和香港联交所上市，2025年末约有33500名全职员工，总部位于北京。",
        "招聘信息验证": "2026-08-03 猎聘公开职位页可检索并显示投递入口，地点北京海淀、20-35k·16薪；职责为萝卜快跑无人驾驶座舱HMI体验与交互设计，要求3年以上交互经验、本科及以上。",
        "备注": "年限与4.5年经验高度匹配，适合有出行、智能座舱、HMI、用户研究或数据驱动迭代经验的候选人，建议优先投递。",
    },
    {
        "平台": "猎聘",
        "岗位名称": "高级交互设计师",
        "公司名称": "京东集团",
        "公司类型": "稳定民企（纳斯达克/港股上市、世界500强）",
        "城市": "北京",
        "薪资范围": "25-35k·14薪",
        "经验要求": "5年以上",
        "学历要求": "本科",
        "岗位链接": "https://www.liepin.com/job/1933370961.shtml",
        "公司工商验证": "京东官方投资者关系页面披露公司在纳斯达克及香港联交所上市，并为《财富》世界500强企业；2025年末京东生态人员规模超过90万。",
        "招聘信息验证": "2026-08-03 猎聘公开职位页仍显示沟通入口，岗位位于北京大兴、25-35k·14薪、招1人；要求5年以上体验设计经验，职责聚焦B端系统交互、数据分析与用户反馈驱动优化，完整沟通通常需登录。",
        "备注": "4.5年与明示门槛仅差半年，可作为冲刺岗位；作品集应重点呈现复杂B端流程、业务目标权衡与上线后的数据迭代。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "AI 产品设计师（交互/视觉方向）短期",
        "公司名称": "安徽晶奇网络科技股份有限公司",
        "公司类型": "稳定民企（新三板挂牌）",
        "城市": "北京",
        "薪资范围": "20-30k/月",
        "经验要求": "经验不限",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC203924720J40995901904.htm",
        "公司工商验证": "安徽晶奇网络科技股份有限公司成立于2006年；公开披露文件显示公司在全国中小企业股份转让系统挂牌，证券简称晶奇网络、证券代码837606，注册地址位于合肥高新区。",
        "招聘信息验证": "2026-07-30 智联招聘公开职位页仍可检索，显示北京昌平区、20-30k/月、本科、全职、招1人；职责覆盖移动端AI办公及通用场景产品的交互与视觉设计，页面可进入投递流程。",
        "备注": "薪资与方向较有吸引力，但职位明确为短期/项目制；投递前应确认合同期限、用工主体、续期可能、社保公积金及驻场安排。",
    },
    {
        "平台": "字节跳动官网",
        "岗位名称": "AI产品设计师 - 剪映CapCut",
        "公司名称": "字节跳动",
        "公司类型": "稳定民企（未上市/10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3-5年",
        "学历要求": "未披露",
        "岗位链接": "https://jobs.bytedance.com/experienced/position/7662384958159980805/detail",
        "公司工商验证": "公开资料可核验字节跳动为北京核心互联网企业，员工规模万人以上；职位主体与投递域名均属于字节跳动官方招聘系统。",
        "招聘信息验证": "2026-07-28 字节跳动官方招聘 API 返回 code=0、channel_online_status=1，职位 ID A181169，发布日期为2026-07-14，地点北京；要求3-5年UX/交互/产品设计经验，官网详情页可直接进入申请流程。",
        "备注": "经验区间与4.5年高度匹配，聚焦AI工具、复杂状态与关键路径设计；有内容创作工具、平台型产品或大模型产品实践者建议优先投递。",
    },
    {
        "平台": "字节跳动官网",
        "岗位名称": "产品设计师（UI方向）-PICO",
        "公司名称": "字节跳动",
        "公司类型": "稳定民企（未上市/10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://jobs.bytedance.com/experienced/position/7547724032134416648/detail",
        "公司工商验证": "公开资料可核验字节跳动为北京核心互联网企业，员工规模万人以上；PICO为字节跳动旗下XR品牌，职位来自官方招聘系统。",
        "招聘信息验证": "2026-07-28 字节跳动官方招聘 API 返回 code=0、channel_online_status=1，职位 ID A236407，地点北京；要求本科及以上、3年以上设计经验，官网详情页当前可直接访问。",
        "备注": "与4.5年经验匹配，强调产品设计全流程、规范建设和跨学科协作；有操作系统、XR、新硬件平台或交互原型经验者更具优势。",
    },
    {
        "平台": "字节跳动官网",
        "岗位名称": "UI设计师-PICO",
        "公司名称": "字节跳动",
        "公司类型": "稳定民企（未上市/10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3年以上",
        "学历要求": "相关专业",
        "岗位链接": "https://jobs.bytedance.com/experienced/position/7553963506556471570/detail",
        "公司工商验证": "公开资料可核验字节跳动为北京核心互联网企业，员工规模万人以上；PICO为字节跳动旗下XR品牌，职位来自官方招聘系统。",
        "招聘信息验证": "2026-07-28 字节跳动官方招聘 API 返回 code=0、channel_online_status=1，职位 ID A18410，地点北京；要求设计、人机交互或计算机相关专业及3年以上相关经验，官网详情页当前可访问。",
        "备注": "和4.5年经验匹配，偏XR/操作系统界面与3D视觉表现；有新硬件平台、空间交互或Unity原型经验者建议重点尝试。",
    },
    {
        "平台": "字节跳动官网",
        "岗位名称": "商业产品高级UX设计师（视觉方向）",
        "公司名称": "字节跳动",
        "公司类型": "稳定民企（未上市/10000人+）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3年以上",
        "学历要求": "未披露",
        "岗位链接": "https://jobs.bytedance.com/experienced/position/7470374386576738568/detail",
        "公司工商验证": "公开资料可核验字节跳动为北京核心互联网企业，员工规模万人以上；职位主体与投递域名均属于字节跳动官方招聘系统。",
        "招聘信息验证": "2026-07-28 字节跳动官方招聘 API 返回 code=0、channel_online_status=1，职位 ID A171016，地点北京；要求3年以上移动互联网设计经验，官网详情页当前可直接访问。",
        "备注": "与4.5年经验匹配，覆盖PC/移动端商业投放平台、视觉风格定义、交互规范和AIGC探索；视觉体系与复杂B端经验强者可优先。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "UI设计师（AI智能营销）(A163318)",
        "公司名称": "北京值得买科技股份有限公司",
        "公司类型": "稳定民企（A股上市）",
        "城市": "北京",
        "薪资范围": "15-20k·13薪",
        "经验要求": "3-5年",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC328489730J40797655409.htm",
        "公司工商验证": "北京值得买科技股份有限公司成立于2011年，2019年登陆深交所创业板（300785）；公司年报与公开招聘页均可核验其上市公司身份。",
        "招聘信息验证": "2026-07-23 智联招聘公开搜索结果当天可访问，显示北京、15-20k·13薪、3-5年；岗位要求本科及以上、2年以上UI或品牌设计经验，职责包括AI智能营销产品界面、视觉与开发落地协作。",
        "备注": "薪资和年限与4.5年经验高度匹配，且业务结合AI智能营销，建议作为北京优先投递岗位。",
    },
    {
        "平台": "智联招聘",
        "岗位名称": "UE设计师(J10878)",
        "公司名称": "南威软件股份有限公司",
        "公司类型": "稳定民企（A股上市）",
        "城市": "北京",
        "薪资范围": "薪资面议",
        "经验要求": "3-5年",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.zhaopin.com/jobdetail/CC455611610J40755944611.htm",
        "公司工商验证": "南威软件股份有限公司为上交所主板上市公司（603636）；公司官网披露全球总部设于北京，主营数字政府、公共安全、社会治理和智慧产业。",
        "招聘信息验证": "2026-07-23 智联招聘公开职位搜索结果仍可访问，显示北京、3-5年；任职要求为本科及以上、3年以上电商/互联网/AI/医疗健康相关UE经验，职责包含交互流程、视觉协作及UE规范沉淀。",
        "备注": "年限与4.5年背景匹配，偏政务及复杂B端产品体验；页面索引发布时间较早，建议投递前先向招聘方确认当前HC。",
    },
    {
        "平台": "猎聘",
        "岗位名称": "资深视觉设计师",
        "公司名称": "孩子王",
        "公司类型": "稳定民企（A股上市/10000人+）",
        "城市": "南京",
        "薪资范围": "15-25k·14薪",
        "经验要求": "",
        "学历要求": "",
        "岗位链接": "https://www.liepin.com/job/1974321525.shtml",
        "公司工商验证": "孩子王儿童用品股份有限公司为 A 股上市公司（301078），注册地与总部在南京；猎聘列表同时标注为已上市、10000 人以上。",
        "招聘信息验证": "2026-07-09 猎聘公开职位页显示原科大讯飞岗位已暂停，但同页推荐列表可公开看到“资深视觉设计师”岗位，城市为南京-江宁区、薪资 15-25k·14薪；完整投递通常需登录。",
        "备注": "南京稳定上市民企新增条目，偏视觉与零售消费场景，适合作为视觉向岗位补充跟进。",
    },
    {
        "平台": "猎聘",
        "岗位名称": "视觉设计高级工程师 (MJ005454)",
        "公司名称": "阳光电源",
        "公司类型": "稳定民企（A股上市/10000人+）",
        "城市": "南京",
        "薪资范围": "薪资面议",
        "经验要求": "",
        "学历要求": "",
        "岗位链接": "https://www.liepin.com/job/1980536237.shtml",
        "公司工商验证": "阳光电源股份有限公司为 A 股上市公司（300274），总部位于合肥，员工规模万人以上。",
        "招聘信息验证": "2026-07-09 猎聘公开职位页显示原科大讯飞岗位已暂停，但同页推荐列表可公开看到“视觉设计高级工程师 (MJ005454)”岗位，城市为南京-江宁区、薪资面议；完整投递通常需登录。",
        "备注": "偏新能源企业品牌与产品视觉协同，属于今天补录的南京稳定大厂岗位。",
    },
    {
        "平台": "字节跳动官网",
        "岗位名称": "产品设计师-TikTok视频创作者方向（北京）",
        "公司名称": "字节跳动",
        "公司类型": "稳定民企（未上市/10000人+）",
        "城市": "北京",
        "薪资范围": "",
        "经验要求": "1年以上",
        "学历要求": "本科及以上",
        "岗位链接": "https://jobs.bytedance.com/experienced/m/position/detail/7330973184173164850?recomId=0b8a4a48-6aa9-11f0-a436-fa163e437cc2&sourceJobId=6940213867608852766",
        "公司工商验证": "公开信息可核验为北京核心互联网企业，员工规模万人以上。",
        "招聘信息验证": "2026-06-18 搜索结果与官方详情页摘要可访问，标题明确为北京岗位，任职要求含本科及以上、1年以上 UX 设计经验。",
        "备注": "本次新增收录；偏创作者工具与发布链路体验，和 4.5 年左右产品/UI 设计背景匹配度较高。",
    },
    {
        "平台": "字节跳动官网",
        "岗位名称": "B端业务平台设计Leader-抖音电商",
        "公司名称": "字节跳动",
        "公司类型": "稳定民企（未上市/10000人+）",
        "城市": "北京",
        "薪资范围": "",
        "经验要求": "",
        "学历要求": "",
        "岗位链接": "https://jobs.bytedance.com/experienced/position/7472677564907030802/detail",
        "公司工商验证": "公开信息可核验为北京核心互联网企业，员工规模万人以上。",
        "招聘信息验证": "2026-06-18 官方招聘搜索结果仍可访问，职位描述明确为抖音电商商家/达人经营平台等 B 端系统设计岗位。",
        "备注": "偏 B 端平台与设计协同管理，职级高于 4.5 年经验，但团队方向和能力要求有参考价值。",
    },
    {
        "平台": "字节跳动官网",
        "岗位名称": "游戏宣发视觉设计师-ONE Studio",
        "公司名称": "字节跳动",
        "公司类型": "稳定民企（未上市/10000人+）",
        "城市": "北京",
        "薪资范围": "",
        "经验要求": "",
        "学历要求": "",
        "岗位链接": "https://jobs.bytedance.com/experienced/position/7629280385859422469/detail",
        "公司工商验证": "公开信息可核验为北京核心互联网企业，员工规模万人以上。",
        "招聘信息验证": "2026-06-18 官方招聘搜索结果仍可访问，职位摘要显示负责广告、H5 落地页与应用商店素材等游戏宣发视觉设计工作。",
        "备注": "更偏视觉与营销物料方向，适合视觉表现力强、做过增长投放素材的人选。",
    },
    {
        "平台": "国聘",
        "岗位名称": "UI设计师",
        "公司名称": "国机数字科技有限公司",
        "公司类型": "央企/国企（国机集团体系）",
        "城市": "北京",
        "薪资范围": "",
        "经验要求": "",
        "学历要求": "本科及以上",
        "岗位链接": "https://www.iguopin.com/job/detail?id=104716979935379693",
        "公司工商验证": "公开信息可核验公司隶属国机集团数字化板块，具备央企体系背景。",
        "招聘信息验证": "2026-07-13 国聘职位详情页仍提示需启用 JavaScript；既有公开摘要显示任职要求含本科及以上及 UI/平面设计经验。",
        "备注": "央企数字科技平台岗位，稳定性强；更适合有品牌视觉与企业数字化产品协同经验的候选人。",
    },
    {
        "平台": "猎聘",
        "岗位名称": "交互体验设计师（UX Designer）(J11861)",
        "公司名称": "鱼跃医疗",
        "公司类型": "稳定民企（A股上市/5000-10000人）",
        "城市": "南京",
        "薪资范围": "12-25k·14薪",
        "经验要求": "5-10年",
        "学历要求": "统招本科",
        "岗位链接": "https://m.liepin.com/job/1974978679.shtml",
        "公司工商验证": "鱼跃医疗为 A 股上市公司（002223），总部位于南京，医疗器械与健康科技业务稳定。",
        "招聘信息验证": "2026-07-13 猎聘职位链接当前可打开但完整信息受安全验证或登录限制；沿用最近一次公开可见摘要，该岗位为南京、12-25k·14薪、5-10年、统招本科。",
        "备注": "南京少见的大厂型 UX 岗，和 4.5 年经验人选接近但略偏资深，值得优先跟进。",
    },
    {
        "平台": "猎聘",
        "岗位名称": "高级体验设计师(MJ005434)",
        "公司名称": "阳光电源",
        "公司类型": "稳定民企（A股上市/10000人+）",
        "城市": "合肥",
        "薪资范围": "薪资面议",
        "经验要求": "6年以上",
        "学历要求": "",
        "岗位链接": "https://m.liepin.com/job/1980458217.shtml?pgRef=c_h5_company_page%3Ac_h5_company_job_listcard%402_80458217%3A1%3Agw.b3d83265-715895426",
        "公司工商验证": "阳光电源为 A 股上市公司（300274），合肥总部，员工规模万人以上。",
        "招聘信息验证": "2026-06-18 猎聘公开职位页仍显示该岗位位于合肥，职位名称和 6 年以上经验要求可核验，完整投递通常需登录。",
        "备注": "偏平台级体验设计与体系建设，虽然门槛略高，但对新能源数字化方向很有价值。",
    },
    {
        "平台": "猎聘",
        "岗位名称": "高级视觉设计师(MJ005466)",
        "公司名称": "阳光电源",
        "公司类型": "稳定民企（A股上市/10000人+）",
        "城市": "合肥",
        "薪资范围": "薪资面议",
        "经验要求": "5年以上",
        "学历要求": "本科",
        "岗位链接": "https://m.liepin.com/job/1980538523.shtml?pgRef=c_h5_company_page%3Ac_h5_company_job_listcard%402_80538523%3A1%3Agw.40d242ef-754577708",
        "公司工商验证": "阳光电源为 A 股上市公司（300274），合肥总部，员工规模万人以上。",
        "招聘信息验证": "2026-06-18 猎聘公开职位页仍显示该岗位位于合肥，本科、5 年以上等摘要信息可访问，完整投递通常需登录。",
        "备注": "偏品牌与产品视觉体系协同，和视觉强项候选人匹配度较高。",
    },
]

DAILY_ADDITION_LINKS = {
    "2026-08-13": {
        "https://talent.baidu.com/jobs/detail/SOCIAL/f66154f6-df92-40c8-b18f-959029a14aeb",
    },
    "2026-08-12": {
        "https://talent.baidu.com/jobs/detail/SOCIAL/8972f75c-6815-4cfe-8793-ad3650c9fac9",
    },
}

INACTIVE_KEYS = {
    (
        "科大讯飞-高级UI设计师（政法业务）",
        "科大讯飞",
        "南京",
        "猎聘",
    ),
    (
        "Senior Product Designer",
        "微软（Microsoft）",
        "北京",
        "LinkedIn",
    ),
}


def latest_seed_csv(target_date: date) -> Path | None:
    candidates: list[tuple[date, Path]] = []
    for base in (DAILY_DIR, DATA_DIR):
        if not base.exists():
            continue
        for path in base.glob("jobs_*.csv"):
            try:
                d = date.fromisoformat(path.stem.replace("jobs_", ""))
            except ValueError:
                continue
            if d < target_date:
                candidates.append((d, path))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


def previous_daily_csv(target_date: date) -> Path | None:
    candidates: list[tuple[date, Path]] = []
    for path in DAILY_DIR.glob("jobs_*.csv"):
        try:
            d = date.fromisoformat(path.stem.replace("jobs_", ""))
        except ValueError:
            continue
        if d < target_date:
            candidates.append((d, path))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


def load_rows(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [{key: row.get(key, "") for key in FIELDS} for row in csv.DictReader(f)]


def load_verified_rows(run_date: str) -> list[dict[str, str]]:
    if not VERIFIED_SOURCE_PATH.exists():
        return []
    payload = json.loads(VERIFIED_SOURCE_PATH.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for item in payload:
        row = {field: "" for field in FIELDS}
        row.update({key: str(value) if value is not None else "" for key, value in item.items()})
        row["日期"] = run_date
        row["是否新增"] = ""
        for field in FIELDS:
            if field in {"日期", "是否新增"}:
                continue
            row[field] = normalize_text(row[field], run_date, preserve_dates=True)
        rows.append(row)
    return rows


def normalize_text(value: str, run_date: str, preserve_dates: bool = False) -> str:
    if not preserve_dates:
        value = re.sub(r"\b20\d{2}-\d{2}-\d{2}\b", run_date, value)
    value = value.replace("今日新增收录；", "")
    value = value.replace("今日新增收录;", "")
    value = value.replace("今天新增发现的", "")
    return value.strip()


def refresh_row(row: dict[str, str], run_date: str) -> dict[str, str]:
    refreshed = {field: row.get(field, "") for field in FIELDS}
    refreshed["日期"] = run_date
    refreshed["是否新增"] = ""
    for field in FIELDS:
        if field in {"日期", "是否新增"}:
            continue
        refreshed[field] = normalize_text(refreshed[field], run_date)
    return refreshed


def unique_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row["岗位名称"].strip(),
        row["公司名称"].strip(),
        normalize_city(row["城市"].strip()),
        row["平台"].strip(),
    )


def link_key(row: dict[str, str]) -> str:
    return row["岗位链接"].strip()


def build_rows(run_date: str, target_date: date) -> list[dict[str, str]]:
    verified_rows = load_verified_rows(run_date)
    seed_rows = [refresh_row(row, run_date) for row in load_rows(latest_seed_csv(target_date))]
    # Once a verified pool exists, use it as the canonical source of truth so
    # stale seed-only rows do not persist across daily regenerations.
    base_rows = verified_rows if verified_rows else seed_rows
    keyed_rows: dict[tuple[str, str, str, str], dict[str, str]] = {}
    seen_links: set[str] = set()
    for row in base_rows:
        link = link_key(row)
        if link and link in seen_links:
            continue
        keyed_rows[unique_key(row)] = row
        if link:
            seen_links.add(link)
    for item in CURATED_ADDITIONS:
        row = {field: "" for field in FIELDS}
        row.update(item)
        row["日期"] = run_date
        row["是否新增"] = ""
        link = link_key(row)
        if link not in seen_links and link not in DAILY_ADDITION_LINKS.get(run_date, set()):
            continue
        if link and link in seen_links and unique_key(row) not in keyed_rows:
            continue
        keyed_rows[unique_key(row)] = row
        if link:
            seen_links.add(link)
    for key in INACTIVE_KEYS:
        keyed_rows.pop(key, None)
    return list(keyed_rows.values())


def load_previous_keys(path: Path | None) -> set[tuple[str, str, str, str]]:
    return {unique_key(row) for row in load_rows(path)}


def load_previous_links(path: Path | None) -> set[str]:
    return {link_key(row) for row in load_rows(path) if link_key(row)}


def normalize_city(value: str) -> str:
    if not value:
        return value
    return value.split("-")[0].split("·")[0].strip()


def tag_new(
    rows: list[dict[str, str]],
    previous_keys: set[tuple[str, str, str, str]],
    previous_links: set[str],
) -> None:
    for row in rows:
        same_link = bool(link_key(row)) and link_key(row) in previous_links
        row["是否新增"] = "否" if same_link or unique_key(row) in previous_keys else "是"


def simplify_company_type(value: str) -> str:
    if "央企" in value:
        return "央企"
    if "国企" in value or "国资" in value:
        return "国企/国资"
    if "外企" in value:
        return "外企"
    return "稳定民企"


def render_dashboard(rows: list[dict[str, str]], run_date: str, compare_basis: str) -> str:
    cities = Counter(row["城市"] for row in rows)
    platforms = Counter(row["平台"] for row in rows)
    company_types = Counter(simplify_company_type(row["公司类型"]) for row in rows)
    payload = []
    for row in rows:
        item = dict(row)
        item["企业大类"] = simplify_company_type(row["公司类型"])
        payload.append(item)
    data_json = json.dumps(payload, ensure_ascii=False)
    city_options = "".join(
        f'<option value="{city}">{city} ({count})</option>'
        for city, count in sorted(cities.items())
    )
    platform_options = "".join(
        f'<option value="{platform}">{platform} ({count})</option>'
        for platform, count in sorted(platforms.items())
    )
    type_options = "".join(
        f'<option value="{kind}">{kind} ({count})</option>'
        for kind, count in sorted(company_types.items())
    )
    total = len(rows)
    new_count = sum(1 for row in rows if row["是否新增"] == "是")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="300">
<title>UI/UX 岗位追踪仪表盘 | {run_date}</title>
<style>
:root {{
  --bg: #f3efe8;
  --paper: #fffaf2;
  --panel: rgba(255,255,255,.82);
  --ink: #1f2b21;
  --muted: #66756b;
  --line: rgba(31,43,33,.12);
  --accent: #0f766e;
  --accent-2: #c2410c;
  --gold: #a16207;
  --new: #b42318;
  --shadow: 0 18px 50px rgba(31,43,33,.08);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: "PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(15,118,110,.16), transparent 32%),
    radial-gradient(circle at top right, rgba(194,65,12,.12), transparent 28%),
    linear-gradient(180deg, #f6f1e8 0%, #efe7db 100%);
}}
.wrap {{ max-width: 1320px; margin: 0 auto; padding: 28px 20px 40px; }}
.hero {{
  background: linear-gradient(135deg, rgba(15,118,110,.92), rgba(23,37,84,.92));
  color: #fff;
  border-radius: 28px;
  padding: 28px;
  box-shadow: var(--shadow);
}}
.hero h1 {{ margin: 0 0 10px; font-size: 34px; line-height: 1.1; }}
.hero p {{ margin: 0; max-width: 880px; opacity: .92; line-height: 1.7; }}
.stats {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin: 18px 0 22px;
}}
.stat {{
  background: var(--panel);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.6);
  border-radius: 22px;
  padding: 18px 18px 16px;
  box-shadow: var(--shadow);
}}
.stat .k {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; }}
.stat .v {{ margin-top: 8px; font-size: 34px; font-weight: 800; }}
.filters {{
  display: grid;
  grid-template-columns: 1.1fr 1fr 1fr 1fr;
  gap: 12px;
  margin-bottom: 18px;
}}
input, select {{
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: rgba(255,255,255,.76);
  min-height: 48px;
  padding: 0 14px;
  color: var(--ink);
  box-shadow: 0 8px 24px rgba(31,43,33,.04);
}}
.result {{
  margin: 8px 0 16px;
  color: var(--muted);
  font-size: 14px;
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 14px;
}}
.card {{
  background: rgba(255,255,255,.84);
  border: 1px solid rgba(255,255,255,.62);
  border-radius: 24px;
  box-shadow: var(--shadow);
  overflow: hidden;
}}
.summary {{
  list-style: none;
  cursor: pointer;
  padding: 18px 18px 16px;
}}
.summary::-webkit-details-marker {{ display: none; }}
.title {{
  font-size: 18px;
  font-weight: 800;
  line-height: 1.35;
  margin-bottom: 10px;
}}
.meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}}
.tag {{
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 12px;
  background: rgba(15,118,110,.08);
  color: var(--accent);
}}
.tag.new {{ background: rgba(180,35,24,.12); color: var(--new); }}
.tag.city {{ background: rgba(161,98,7,.12); color: var(--gold); }}
.company {{ font-weight: 700; }}
.brief {{ color: var(--muted); line-height: 1.65; font-size: 14px; }}
.detail {{
  border-top: 1px solid var(--line);
  padding: 0 18px 18px;
  line-height: 1.7;
  font-size: 14px;
}}
.detail strong {{ color: var(--ink); }}
.detail a {{ color: var(--accent); }}
.empty {{
  display: none;
  background: rgba(255,255,255,.84);
  border-radius: 24px;
  padding: 40px 18px;
  text-align: center;
  color: var(--muted);
  box-shadow: var(--shadow);
}}
@media (max-width: 980px) {{
  .stats, .filters {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}
@media (max-width: 640px) {{
  .hero h1 {{ font-size: 28px; }}
  .stats, .filters {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>UI/UX 设计师岗位追踪</h1>
      <p>更新时间：{run_date}。覆盖北京、南京、安徽省公开可核验职位；支持按城市、企业类型、平台筛选，卡片点击展开详情，所有数据已内嵌，可离线查看。新增标记基于最近一期历史日表 {compare_basis}。</p>
    </section>
    <section class="stats">
      <div class="stat"><div class="k">岗位总数</div><div class="v">{total}</div></div>
      <div class="stat"><div class="k">今日新增</div><div class="v">{new_count}</div></div>
      <div class="stat"><div class="k">覆盖城市</div><div class="v">{len(cities)}</div></div>
      <div class="stat"><div class="k">数据平台</div><div class="v">{len(platforms)}</div></div>
    </section>
    <section class="filters">
      <input id="searchInput" type="text" placeholder="搜索岗位、公司、备注" oninput="render()">
      <select id="cityFilter" onchange="render()"><option value="">全部城市</option>{city_options}</select>
      <select id="typeFilter" onchange="render()"><option value="">全部企业类型</option>{type_options}</select>
      <select id="platformFilter" onchange="render()"><option value="">全部平台</option>{platform_options}</select>
    </section>
    <div class="result" id="resultCount"></div>
    <section class="grid" id="grid"></section>
    <section class="empty" id="empty">没有匹配结果，调整筛选条件后再试。</section>
  </div>
<script>
const DATA = {data_json};

function card(row) {{
  return `
    <details class="card">
      <summary class="summary">
        <div class="title">${{row["岗位名称"]}}</div>
        <div class="meta">
          <span class="tag city">${{row["城市"]}}</span>
          <span class="tag">${{row["平台"]}}</span>
          <span class="tag">${{row["企业大类"]}}</span>
          <span class="tag new">${{row["是否新增"] === "是" ? "今日新增" : "历史延续"}}</span>
        </div>
        <div class="company">${{row["公司名称"]}}</div>
        <div class="brief">${{row["备注"]}}</div>
      </summary>
      <div class="detail">
        <div><strong>公司类型：</strong>${{row["公司类型"]}}</div>
        <div><strong>薪资范围：</strong>${{row["薪资范围"] || "未公开"}}</div>
        <div><strong>经验要求：</strong>${{row["经验要求"] || "未公开"}}</div>
        <div><strong>学历要求：</strong>${{row["学历要求"] || "未公开"}}</div>
        <div><strong>公司工商验证：</strong>${{row["公司工商验证"]}}</div>
        <div><strong>招聘信息验证：</strong>${{row["招聘信息验证"]}}</div>
        <div><strong>投递链接：</strong><a href="${{row["岗位链接"]}}" target="_blank" rel="noopener">打开职位</a></div>
      </div>
    </details>
  `;
}}

function render() {{
  const search = document.getElementById("searchInput").value.trim().toLowerCase();
  const city = document.getElementById("cityFilter").value;
  const type = document.getElementById("typeFilter").value;
  const platform = document.getElementById("platformFilter").value;

  const rows = DATA.filter((row) => {{
    if (city && row["城市"] !== city) return false;
    if (type && row["企业大类"] !== type) return false;
    if (platform && row["平台"] !== platform) return false;
    if (search) {{
      const hay = `${{row["岗位名称"]}} ${{row["公司名称"]}} ${{row["备注"]}} ${{row["公司工商验证"]}}`.toLowerCase();
      if (!hay.includes(search)) return false;
    }}
    return true;
  }}).sort((a, b) => {{
    if (a["是否新增"] !== b["是否新增"]) return a["是否新增"] === "是" ? -1 : 1;
    return `${{a["城市"]}}-${{a["公司名称"]}}`.localeCompare(`${{b["城市"]}}-${{b["公司名称"]}}`, "zh-CN");
  }});

  document.getElementById("resultCount").textContent = `当前显示 ${{rows.length}} / ${{DATA.length}} 条`;
  document.getElementById("grid").innerHTML = rows.map(card).join("");
  document.getElementById("empty").style.display = rows.length ? "none" : "block";
}}

render();
setInterval(() => location.reload(), 300000);
</script>
</body>
</html>
"""


def render_report(rows: list[dict[str, str]], run_date: str, compare_basis: str) -> str:
    by_city = Counter(row["城市"] for row in rows)
    by_platform = Counter(row["平台"] for row in rows)
    by_company_type = Counter(simplify_company_type(row["公司类型"]) for row in rows)
    new_rows = [row for row in rows if row["是否新增"] == "是"]
    top_new = "\n".join(
        f"- {row['城市']}｜{row['公司名称']}｜{row['岗位名称']}｜{row['平台']}｜{row['岗位链接']}"
        for row in new_rows[:10]
    ) or "- 无新增岗位"
    new_insights = "\n".join(
        f"- **{row['公司名称']}｜{row['岗位名称']}**：{row['备注']}"
        for row in new_rows[:5]
    ) or "- 今日无新增，建议继续优先复核存量岗位的有效性与投递状态。"
    city_lines = "\n".join(f"- {city}: {count} 条" for city, count in sorted(by_city.items()))
    platform_lines = "\n".join(
        f"- {platform}: {count} 条" for platform, count in sorted(by_platform.items())
    )
    company_type_lines = "\n".join(
        f"- {company_type}: {count} 条"
        for company_type, count in sorted(by_company_type.items())
    )
    compare_note = (
        f"- 本次按 `data/daily/{compare_basis}` 进行新增比对。"
        if compare_basis != "无历史文件"
        else "- 首次运行，无历史日表可比，全部岗位标记为新增。"
    )
    return f"""# UI/UX 设计师岗位日报 - {run_date}

## 今日概览
- 岗位总数：{len(rows)}
- 今日新增：{len(new_rows)}
- 对比基准：{compare_basis}
- 覆盖城市：{", ".join(sorted(by_city))}

## 城市分布
{city_lines}

## 平台分布
{platform_lines}

## 企业类型分布
{company_type_lines}

## 今日新增岗位
{top_new}

## 今日新增解读
{new_insights}

## 执行说明
- {compare_note[2:]}
- 字节跳动岗位优先按官方招聘页或官方搜索摘要复核；国聘职位页需要 JavaScript 才能完整渲染，但搜索结果摘要仍可验证职位真实性。
- LinkedIn、猎聘部分岗位可公开查看摘要和部分职责，完整投递或更多详情通常需要登录。
- BOSS直聘公开网页索引不稳定，未将无法独立核验企业门槛与有效投递入口的搜索摘要写入结果；智联招聘的公开详情页可核验岗位已保留。
- 51job 今日公开页存在频繁验证与反爬拦截，本次仅保留可公开核验且企业背景明确的职位，未将无法稳定复核的条目写入结果。
"""


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    run_date_env = os.environ.get("RUN_DATE")
    target_date = date.fromisoformat(run_date_env) if run_date_env else date.today()
    run_date = target_date.isoformat()
    rows = build_rows(run_date, target_date)
    prev_path = previous_daily_csv(target_date)
    previous_keys = load_previous_keys(prev_path)
    previous_links = load_previous_links(prev_path)
    tag_new(rows, previous_keys, previous_links)
    rows.sort(key=lambda row: (row["是否新增"] != "是", row["城市"], row["平台"], row["公司名称"], row["岗位名称"]))

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = DATA_DIR / f"jobs_{run_date}.csv"
    daily_path = DAILY_DIR / f"jobs_{run_date}.csv"
    report_path = DATA_DIR / f"日报_{run_date}.md"
    html_path = DATA_DIR / "jobs_dashboard.html"
    json_path = DATA_DIR / "all_jobs.json"

    compare_basis = prev_path.name if prev_path else "无历史文件"

    write_csv(csv_path, rows)
    write_csv(daily_path, rows)
    report_path.write_text(render_report(rows, run_date, compare_basis), encoding="utf-8")
    html_path.write_text(render_dashboard(rows, run_date, compare_basis), encoding="utf-8")
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(rows)} rows to {csv_path}")
    print(f"Wrote backup CSV to {daily_path}")
    print(f"Wrote report to {report_path}")
    print(f"Wrote dashboard to {html_path}")


if __name__ == "__main__":
    main()
