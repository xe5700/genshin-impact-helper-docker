<div align="center"> 
<h1 align="center">
Genshin Impact Helper
</h1>

![Genshin Impact Helper](https://i.loli.net/2020/11/18/3zogEraBFtOm5nI.jpg)
[![GitHub stars](https://img.shields.io/github/stars/y1ndan/genshin-impact-helper?style=flat-square)](https://github.com/y1ndan/genshin-impact-helper/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/y1ndan/genshin-impact-helper?style=flat-square)](https://github.com/y1ndan/genshin-impact-helper/network)
[![GitHub issues](https://img.shields.io/github/issues/y1ndan/genshin-impact-helper?style=flat-square)](https://github.com/y1ndan/genshin-impact-helper/issues)
[![GitHub contributors](https://img.shields.io/github/contributors/y1ndan/genshin-impact-helper?style=flat-square)](https://github.com/y1ndan/genshin-impact-helper/graphs/contributors)
[![QQ Group](https://img.shields.io/badge/chat-130516740-0d86d7?style=flat-square)](https://qm.qq.com/cgi-bin/qm/qr?k=_M9lYFxkYD7yQQR2btyG3pkZWFys_I-l&authKey=evGDzE2eFVBm46jsHpgcWrokveg70Z9GKl3H45o0oJuia620UGeO27lDPG9gKb/2&noverify=0)
![Github workflow status](https://img.shields.io/github/workflow/status/y1ndan/genshin-impact-helper/Genshin%20Impact%20Helper?label=status&style=flat-square)

</div>

## 💭前言

> 吹水交流：[130516740](https://qm.qq.com/cgi-bin/qm/qr?k=_M9lYFxkYD7yQQR2btyG3pkZWFys_I-l&authKey=evGDzE2eFVBm46jsHpgcWrokveg70Z9GKl3H45o0oJuia620UGeO27lDPG9gKb/2&noverify=0)

原神是我见过的唯一一个游戏本体和签到福利分离的游戏，玩家为了签到还要额外下载米游社 App。

平心而论，目前的每日签到奖励真的不咋地，都知道是蚊子腿。事实上，你完全可以选择无视签到，不签也没啥大的损失；或者选择手动签到，但这样的话哪天忘记打卡了就很头疼。

我承认是馋了这 **6W+** 摩拉和紫色经验书的奖励，于是撸了这个项目，实现自动每日签到。

**如果觉得本项目对你有帮助，请顺手点个`Star`吧QAQ ♥**

## 🌀简介

Genshin Impact Helper 可以自动化为你获取原神每日福利。

## 💡特性

- [x] **自动签到**  程序会在每天早上自动执行签到流程，也可以随时通过部署教程的`步骤4`手动触发，具体时间参照[此处](.github/workflows/main.yml)
- [x] **支持订阅**  通过配置`SCKEY`开启订阅，每天将签到结果推送到微信上
- [x] **支持多账号**  不同账号的`Cookie`之间用`#`分隔，如：`yourCookie1#yourCookie2`
- [x] **支持多角色**  支持绑定官服和B站渠道服角色的米游社账号

## 📐部署

<details>
<summary>查看教程</summary>

### 1. Fork 仓库

- 项目地址：[github/genshin-impact-helper](https://github.com/y1ndan/genshin-impact-helper)
- 点击右上角`Fork`到自己的账号下

> ![fork](https://i.loli.net/2020/10/28/qpXowZmIWeEUyrJ.png)

### 2. 获取 Cookie

浏览器打开 https://bbs.mihoyo.com/ys/ 并登录账号

#### 2.1 方法一

- 按`F12`，打开`开发者工具`，找到`Network`并点击
- 按`F5`刷新页面，按下图复制`Cookie`

> ![cookie](https://i.loli.net/2020/10/28/TMKC6lsnk4w5A8i.png)

#### 2.2 方法二

- 复制以下代码

```
var cookie = document.cookie;
var ask = confirm('Cookie:' + cookie + '\n\n是否复制内容到剪切板？');
if (ask == true) {
    copy(cookie);
    msg = cookie;
} else {
    msg = 'Cancel';
}
```

- 按`F12`，打开`开发者工具`，找到`Console`并点击
- 命令行粘贴代码并运行，获得类似`Cookie:xxxxxx`的输出信息
- `xxxxxx`部分即为所需复制的`Cookie`，点击确定复制

### 3. 添加 Cookie 至 Secrets

- 回到项目页面，依次点击`Settings`-->`Secrets`-->`New secret`

> ![new-secret.png](https://i.loli.net/2020/10/28/sxTuBFtRvzSgUaA.png)

- 建立名为`COOKIE`的 secret，值为`步骤2`中复制的`Cookie`内容，最后点击`Add secret`

- secret名字必须为`COOKIE`！
- secret名字必须为`COOKIE`！
- secret名字必须为`COOKIE`！

> ![add-secret](https://i.loli.net/2020/10/28/sETkVdmrNcCUpgq.png)

### 4. 启用 Actions

> Actions 默认为关闭状态，Fork 之后需要手动执行一次，若成功运行其才会激活。

返回项目主页面，点击上方的`Actions`，再点击左侧的`Genshin Impact Helper`，再点击`Run workflow`
    
> ![run](https://i.loli.net/2020/10/28/5ylvgdYf9BDMqAH.png)

</details>

至此，部署完毕。

## 🔍结果

当你完成上述流程，可以在`Actions`页面点击`Genshin Impact Helper`-->`build`-->`Run sign`查看结果。

<details>
<summary>查看结果</summary>

### 签到成功

如果成功，会输出类似`"result": "Success"`的信息：

```
2020-11-18T22:11:45 INFO Sleep for 100 seconds ...
2020-11-18T22:13:26 INFO UID is 100***000
2020-11-18T22:13:27 INFO {
  "result": "Success",
  "message": "{\"retcode\": 0, \"message\": \"OK\", \"data\": {\"code\": \"ok\"}}"
}
```

### 签到失败

如果失败，会输出类似`"result": "Failed"`的信息：

```
2020-11-17T22:11:33 INFO Sleep for 54 seconds ...
2020-11-17T22:12:28 INFO UID is 100***000
2020-11-17T22:12:29 INFO {
  "result": "Failed",
  "message": "{\"data\": null, \"message\": \"请求异常\", \"retcode\": -401}"
}
Error: Process completed with exit code 255.
```

同时你会收到一封来自GitHub、标题为`Run failed: Genshin Impact Helper - master`的邮件。

</details>

## 🔔订阅

若开启订阅推送，无论成功与否，都会收到微信通知。

- 使用 GitHub 登录 [sc.ftqq.com](http://sc.ftqq.com/?c=github&a=login) 创建账号
- 点击「[发送消息](http://sc.ftqq.com/?c=code)」，获取`SCKEY`
- 点击「[微信推送](http://sc.ftqq.com/?c=wechat&a=bind)」，完成微信绑定
- 建立名为`SCKEY`的 secret，并添加获取的 SCKEY 值，开启订阅推送

## ❗️协议

使用 Genshin Impact Helper 即表明，您知情并同意：

- 此代码通过模拟浏览器使用 Cookies 登录米游社网页，点击页面完成签到来实现签到。功能通过官方公开的 API 实现，并非游戏外挂
- 用户之 Cookie 被储存于 Github 服务器，只供本项目使用。若 Github 服务器被攻破，则您的 Cookie 有遭到泄露的风险。除此之外，开发者无权获取您的 Cookie；即使是用户，一旦创建完成`Secrets`，也无法再次从中查看 Cookie
- Genshin Impact Helper 不会对您的任何损失负责，包括但不限于奖励回收、账号异常、刻晴被削、矿产被挖、核弹爆炸、第三次世界大战等
