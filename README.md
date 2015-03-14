## 介绍

这几个脚本主要利用来自 http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest 的数据生成路由命令脚本, 让vpn客户端在进行连接的时候自动执行. 通过这些路由脚本, 可以让用户在使用vpn作为默认网络网关的时候, 不使用vpn进行对中国国内ip的访问, 从而减轻vpn的负担, 和增加访问国内网站的速度.

## 基本约定

在使用这些脚本之前, 请确保你在自己的电脑上已经成功配置好一个vpn连接(pptp 或者 openvpn), 并且让之以默认网络网关的方式运行, 这通常也是默认配置, 即vpn接入之后所有网络流量都通过vpn进行.

## OpenVPN

使用此法之前, 请确认openvpn版本是否为 v2.1 或者以上, 如果不是请参看下方不同系统关于openvpn部分的描述

### 客户端设置

本方法适用于使用openvpn v2.1或更高版本的用户. 因为openvpn v2.1比之前版本增加了一个名为max-routes的新参数, 通过设置该参数, 我们可以在配置文件里(服务端, 客户端)直接添加超过100条以上的路由信息. 具体设置步骤如下:

1. 下载 chnroutes.py 文件
 在命令行里执行 python chnroutes.py, 这将生成一个名为 routes.txt 的文本文件. 对于不想安装python的用户, 可以直接从项目下来列表里下载该文件. 它将会每月更新一次.
2. 使用你喜欢的文本编辑器打开上述文件, 并把内容复制粘贴到openvpn配置文件的末尾
3. 同时在openvpn配置文件的头部添加一句 max-routes num, 其中num是一个不小于文件routes.txt的行数的数字, 实际上因为还有一些服务器端push过来的路由信息, 所以保险起见可以用 routes.txt的行数加上50, 比如目前得到的routes.txt的行数是940, 你可以把数字设置为1000: max-routes 1000
4. 修改完之后, 重新进行openvpn连接, 你可以用之前描述过的方法进行测试是否成功 

以上方法在Mac OSX, Linux 和 Windows上测试通过. 但需要注意的是, 这里用到一个net_gateway的变量表示未连接openvpn前的网关地址, 但openvpn的文档里有说明这个不是所有系统都支持的, 如果发生这个情况, 可以修改一下生成脚本, 把net_gateway修改为你的局域网的网关地址. 对于windows 7 和 vista, OpenVPN的windows客户端可能需要设置Windows XP兼容模式才能使用, 安装文件要在属性选择中的兼容性选择Windows XP和以管理员的身份运行，安装好的运行文件也同样选择这两个选项。如果还是不能连接到VPN的网络，可以尝试在配置文件中加入：

```
route-method exe
route-delay 2
```

### 注意事项

* 因为这些ip数据不是固定不变的, 尽管变化不大, 但还是建议每隔两三个月更新一次
* 使用此法之后, 可能会导致google music无法访问, 这个其实是因为连上vpn之后, 使用的dns也是国外的, 国外dns对google.cn 解析出来的是国外的ip, 所以一个简单的解决方法是修改本机的hosts文件, 把国内dns解析出来的google.cn的地址写上去: 203.208.39.99 www.google.cn google.cn 

## PPTP

### Mac OSX

* 下载 chnroutes.py
* 从终端进入下载目录, 执行 `python chnroutes.py -p mac`, 执行完毕之后同一目录下将生成两个新文件'ip-up'和'ip-down'
* 把这两个文件copy到 `/etc/ppp` 目录, 并使用 `sudo chmod a+x ip-up ip-down` 命令把它们设置为可执行
* 设置完毕, 重新连接vpn. 测试步骤同上. 

### Linux

* 下载 chnroutes.py
* 从终端进入下载目录, 执行 `python chnroutes.py -p linux`, 执行完毕之后同一目录下将生成两个新文件'ip-pre-up'和'ip-down'.
* 把 `ip-pre-up` 拷贝到 `/etc/ppp` 目录, `ip-down` 拷贝到 `/etc/ppp/ip-down.d` 目录. 测试步骤同上. 

### Windows

* 下载 chnroutes.py
* 从终端进入下载目录, 执行 `python chnroutes.py -p win`, 执行之后会生成vpnup.bat和vpndown.bat两个文件. 

由于windows上的pptp不支持拨号脚本, 所以也只能在进行拨号之前手动执行vpnup.bat文件以设置路由表. 而在断开vpn之后, 如果你觉得有必要, 可以运行vpndown.bat把这些路由信息给清理掉.

如果机器上没有安装python, 可以直接从下载页面上下载已经预生成的bat文件.

### Android

由于没在android上进行过测试, 无法确定上文描述的openvpn v2.1的使用方法是否也在android手机上适用, 所以保留以下内容

#### openvpn


* 下载 chnroutes.py
* 从终端进入下载目录, 执行 `python chnroutes.py -p linux`, 这将成
  'vpnup.sh'和'vpndown.sh'两个文件.
* 把步骤2生成的两个文件拷贝到 android 的 /sdcard/openvpn/目录下, 然后修改openvpn配置文件, 
  在文件中加上以上三句:
  
  ``` 
  script-security 2
  up "/system/bin/sh /sdcard/openvpn/vpnup.sh"
  down "/system/bin/sh /sdcard/openvpn/vpndown.sh"
  ```
 
  注意自行修改其中的路径以符合你的android rom的实际路径 

另外, 这里假定了你的android已经安装过busybox, 否则请先安装busybox再进行以上操作, 还需要知道的是, 这个脚本在手机上执行会花费比较长的时间, 如非必要, 就不要用了. 也许采用非redirect-gateway方式, 然后在ovpn配置文件里添加几条需要路由的ip段是比较快捷方便的做法.
基于Linux的第三方系统的路由器

一些基于Linux系统的第三方路由器系统如: OpenWRT, DD-WRT, Tomato 都带有VPN(PPTP/Openvpn)客户端的, 也就是说, 我们只需要在路由器进行VPN拨号, 并利用本项目提供的路由表脚本就可以把VPN针对性翻墙扩展到整个局域网. 当然, 使用这个方式也是会带来副作用, 即局域网的任何机器都不适合使用Emule或者BT等P2P下载软件. 但对于那些不使用P2P, 希望在路由器上设置针对性翻墙的用户, 这方法十分有用, 因为只需要一个VPN帐号, 局域网内的所有机器, 包括使用wifi的手机都能自动翻墙. 相信配置方式请参考: Autoddvpn 项目.

## 信息反馈

本项目的脚本都是在使用路由器进行拨号的情况下测试通过的, 如果在其它拨号方式下, 脚本不能运作, 请添加一个新的issue. 另外, 在配合openvpn使用的时候, 可能会出现一种情况是因为网络质量不好, openvpn非主动断开, 这时候vpndown脚本也会被自动调用, 但重新连上之后, 可能会找不到默认的路由而添加失败, 这时候你可以通过停止openvpn重连, 并手动设置好原来的默认路由再重新进行openvpn拨号. 