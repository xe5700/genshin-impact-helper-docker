<div align="center"> 
<h1 align="center">
Genshin Impact Helper
</h1>

![Genshin Impact Helper](https://i.loli.net/2020/11/18/3zogEraBFtOm5nI.jpg)
[![GitHub stars](https://img.shields.io/github/stars/y1ndan/genshin-impact-helper?style=flat-square)](https://github.com/y1ndan/genshin-impact-helper/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/y1ndan/genshin-impact-helper?style=flat-square)](https://github.com/y1ndan/genshin-impact-helper/network)
[![GitHub issues](https://img.shields.io/github/issues/y1ndan/genshin-impact-helper?style=flat-square)](https://github.com/y1ndan/genshin-impact-helper/issues)
[![GitHub contributors](https://img.shields.io/github/contributors/y1ndan/genshin-impact-helper?style=flat-square)](https://github.com/y1ndan/genshin-impact-helper/graphs/contributors)
![Github workflow status](https://img.shields.io/github/workflow/status/y1ndan/genshin-impact-helper/Genshin%20Impact%20Helper?label=status&style=flat-square)

</div>

## 📎前言

原神是我见过的唯一一个游戏本体和签到福利分离的游戏，玩家为了签到还要额外下载米游社 App。

平心而论，目前的每日签到奖励真的不咋地，都知道是蚊子腿。事实上，你完全可以选择无视签到，不签也没啥大的损失；或者选择手动签到，但这样的话哪天忘记打卡了就很头疼。

我承认是馋了这 **6W+** 摩拉和紫色经验书的奖励，于是撸了这个项目，实现自动每日签到。

**如果觉得本项目对你有帮助，顺手点个 `Star` 吧QAQ❤**

## 📐部署

### 1. Fork 仓库

* 项目地址：[github/genshin-impact-helper](https://github.com/y1ndan/genshin-impact-helper)
* 点击右上角`Fork`到自己的账号下

> ![fork](https://i.loli.net/2020/10/28/qpXowZmIWeEUyrJ.png)

### 2. 获取 Cookie

浏览器打开 https://bbs.mihoyo.com/ys/ 并登录账号

#### 2.1 方法一

* 按`F12`，打开`开发者工具`，找到`Network`并点击
* 按`F5`刷新页面，按下图复制`Cookie`

> ![cookie](https://i.loli.net/2020/10/28/TMKC6lsnk4w5A8i.png)

#### 2.2 方法二

* 复制以下代码
```
JSON.stringify({
  Cookie: document.cookie
});
```
* 按`F12`，打开`开发者工具`，找到`Console`并点击
* 命令行粘贴代码并运行，获得类似`"{"Cookie":"xxxxxx"}"`的输出信息
* `xxxxxx`部分即为所需复制的`Cookie`

### 3. 添加 Cookie 至 Secrets

* 回到项目页面，依次点击`Settings`-->`Secrets`-->`New secret`

> ![new-secret.png](https://i.loli.net/2020/10/28/sxTuBFtRvzSgUaA.png)

* 建立名为`COOKIE`的 secret，值为`步骤2`中复制的`Cookie`内容，最后点击`Add secret`

> ![add-secret](https://i.loli.net/2020/10/28/sETkVdmrNcCUpgq.png)

### 4. 启用 Actions

> Actions 默认为关闭状态，Fork 之后需要手动执行一次，若成功运行其才会激活。

返回项目主页面，点击上方的`Actions`，再点击左侧的`Genshin Impact Helper`，再点击`Run workflow`
    
> ![run](https://i.loli.net/2020/10/28/5ylvgdYf9BDMqAH.png)

至此，部署完毕。

## 🔍结果

当你完成上述流程，可以在`Actions`页面点击`Genshin Impact Helper`-->`build`-->`run sign`查看结果。

如果成功，会输出类似`"result": "Success"`的信息：

```
2020-10-30T11:30:08 INFO sleep for 214 seconds ...
2020-10-30T11:30:08 INFO UID is 100***001
2020-10-30T11:30:09 INFO {
  "result": "Success",
  "message": "{'data': None, 'message': '旅行者,你已经签到过了', 'retcode': -5003}"
}
```

如果失败，会输出类似`"result": "Failed"`的信息：

```
2020-10-30T11:14:26 INFO sleep for 207 seconds ...
2020-10-30T11:14:26 ERROR get uid failed, request is "{'data': None, 'message': '登录失效，请重新登录', 'retcode': -100}"
2020-10-30T11:14:26 INFO {
  "result": "Failed",
  "message": ""{'data': None, 'message': '登录失效，请重新登录', 'retcode': -100}""
}
```

## ❗️注意

1. 程序会在每天早上自动执行签到流程，也可以随时通过上述`步骤4`手动触发
2. 登录失效时，尝试重新更换`Cookie` 
3. 支持多账号，不同`Cookie`之间用`#`分开即可
4. 支持官服和 B 服

