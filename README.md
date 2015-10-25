chnroutes
=========

这几个脚本主要利用来自 [APNIC Delegated List] 的数据生成路由命令脚本, 让 VPN 客户端
在进行连接的时候自动执行。通过这些路由脚本, 可以让用户在使用 VPN 作为默认网络网关时 
不使用 VPN 进行对中国国内 IP 的访问, 从而减轻 VPN 的负担, 和增加访问国内网站的速度。

For English service, press 2 and read README.en.md.

基本约定
--------

在使用这些脚本之前, 请确保你在自己的电脑上已经成功配置好一个 VPN 连接（PPTP/OpenVPN）, 
并且让之以默认网络网关的方式运行, 这通常也是默认配置, 即 VPN 接入之后所有网络流量都通过
VPN 进行。

要验证设置是否生效，可以使用诸如 ip.cn 的国内网站。对于需要使用 Android 的地方，我们也
提供预先生成的文件。

OpenVPN 配置
------------

使用此法之前, 请确认 OpenVPN 版本是否为 v2.1 或者以上, 如果不是请参看下方不同
系统关于 OpenVPN 部分的描述。如果你使用 Android，请往后读。

OVPN v2.1 比之前版本增加了一个 `max-routes` 可以用来在配置文件里（服务端和客户端）
直接添加超过 100 条以上的路由信息。具体设置步骤如下（在 OS X, Linux 和 Windows
上测试通过）:

1. 获取 `routes.txt` 路由列表
  - 下载 `chnroutes.py`，然后执行命令 `python chnroutes.py` 生成。
2. 把 `routes.txt` 的内容复制粘贴到 OpenVPN 配置文件的末尾。
3. 同时在 OpenVPN 配置文件的头部添加一句 `max-routes NUM`, 其中 NUM 是一个不小于
   `routes.txt` 行数的数字。考虑到还有一些服务器端 push 过来的路由信息, 保险起见可用
   `routes.txt` 行数加上 50, 比如目前得到的 `routes.txt` 行数是 940, 你可以把数字
   设置为 1000: `max-routes 1000`
4. 修改完之后, 重新进行 OpenVPN 连接并测试。

如果你的 OpenVPN 版本低于 2.1 并且没法升级，你可以尝试[合并 IP 条目][chinaip]或者
参考后面的 Android 解法。

### 注意事项

* 这里用到 `net_gateway` 变量表示连接 OpenVPN 前的网关地址, 但 OpenVPN 文档提到不是
  所有系统都支持这个变量。如果发生这个情况, 可以修改一下生成脚本, 把 `net_gateway` 手动
  修改为你的局域网的网关地址。
* 对于 Windows Vista+, OpenVPN 的 Windows 客户端可能需要设置 Windows XP 兼容模式才能
  使用。安装文件要在属性选择中的兼容性选择 Windows XP 和以管理员的身份运行，安装好的运行
  文件也同样选择这两个选项。如果还是不能连接到VPN的网络，可以尝试在配置文件中加入：
  ```Bash
  route-method exe
  route-delay 2
  ```
* 有时网络质量不好, OpenVPN 非主动断开, 这时候 vpndown 脚本也会被自动调用。重新连上之后, 
  又可能会找不到默认的路由而添加失败。这时候你可以停止 OpenVPN 重连, 并手动设置好原来的
  默认路由再重新进行 OpenVPN 拨号。

### Android & OpenVPN < 2.1

由于没在 Android 上进行过测试, 无法确定上文描述的 OpenVPN 2.1 的使用方法是否也在
Android 手机上适用, 所以保留以下内容。这个方式直接使用 OpenVPN 的脚本运行功能，原理上
类似接下来的 PPTP 方法。

1. 下载 `chnroutes.py`。
2. 从终端进入下载目录, 执行 `python chnroutes.py -p android`, 这将生成 `vpnup.sh` 和
  `vpndown.sh` 两个文件.
3. 把生成的两个文件拷贝到 `/sdcard/openvpn/` 目录下, 然后修改 OpenVPN 配置文件, 
  在文件中加上以上三句:
  ```
  script-security 2
  up "/system/bin/sh /sdcard/openvpn/vpnup.sh"
  down "/system/bin/sh /sdcard/openvpn/vpndown.sh"
  ```
  你可以自行修改 `sh` 和 `vpn{up,down}.sh` 的位置来契合你的实际情况。

这里假定你的 Android 有命令 `netstat`, `grep` 和 `route`。你可以使用 busybox 达成
这点。

由于 IP [数量众多][chinaip]，要打开 `route` 命令很多次，这个脚本[用时不短][PR48]，
如果不必要的话就不要用了。也许采用非 redirect-gateway 方式, 然后在 OVPN 配置文件里添加
几条需要路由的 IP 段是比较快捷方便的做法.

PPTP 用法
---------

这些用法中生成的脚本都是通用的，也就是说你也可以用在 PPTP 之外的地方。

### OS X / Linux

1. 下载 `chnroutes.py`。
2. `python chnroutes.py -p "$(uname)"`; chmod a+x ip-*; sudo cp ip-* /etc/ppp`.
  - 如果你已有其他文件，你可能更想要将生成的那些文件加入已有文件的末尾。
3. 设置完毕。重新连接 VPN，测试步骤同上。

### Windows

* 下载 `chnroutes.py`。
* 从终端进入下载目录, 执行 `python chnroutes.py -p win`, 执行之后会生成 `vpnup.bat`
和 `vpndown.bat` 两个文件。

由于 Windows 不支持 PPTP 拨号脚本，只能在进行拨号之前手动执行 `vpnup.bat` 设置路由表。
在断开 VPN 之后, 如果你觉得有必要, 可以运行 `vpndown.bat` 把这些路由信息给清理掉。

如果机器上没有安装 Python, 可以直接从下载页面上下载已经预生成的 bat 文件。

在路由器上使用
--------------

一些基于 Linux 系统的第三方路由器系统，如 OpenWRT, DD-WRT, Tomato 都带有我们所需的客
户端。我们只需要在路由器进行 VPN 拨号, 并利用本项目提供的路由表脚本就可以把 VPN 针对性
翻墙扩展到整个局域网。对于那些不使用 P2P, 希望在路由器上设置针对性翻墙的用户, 这方法
十分有用, 因为只需要一个 VPN 帐号, 局域网内的所有机器包括使用 Wifi 的手机都能自动翻墙。

[autoddvpn] 可以提供这样的处理方案。请注意这样会使得即局域网的任何机器都不适合使用
emule, BT 等 P2P 下载软件（P2P 流量不应穿过 VPN）。


注意事项
--------

* 这些 IP 数据不是固定不变的, 尽管变化不大, 但还是建议每隔两三个月更新一次。
* 使用此法之后, 可能会导致 Google Music 无法访问, 这个其实是因为连上 VPN 之后, 使用的
  DNS 也是国外的, 国外 DNS 对 google.cn 解析出来的是国外的 IP, 所以一个简单的解决方法是
  修改本机的 hosts 文件, 把国内 DNS 解析出来的 google.cn 的地址写上去:
  ```
  # Google.cn, from Chinese DNS
  203.208.39.99 www.google.cn google.cn
  ```


信息反馈
--------

本项目的脚本都是在使用路由器进行拨号的情况下测试通过的。如果在其它拨号方式下脚本不能运作, 
请添加一个新的 Issue。

[APNIC Delegated List]:https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest
[chinaip]:https://github.com/liudongmiao/chinaip
[PR48]:https://github.com/fivesheep/chnroutes/pull/48
[autoddvpn]:https://github.com/lincank/autoddvpn