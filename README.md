# 极星量化终端

#### 介绍
1. 极星量化终端基于python开发，结合极星9.5PC版使用，运行在Windows7及系统以上x64平台上
2. 量化交易者可使用极星量化终端编写策略、加载策略进行回测，并根据回测报告掌握策略盈亏情况。
3. 量化交易者可使用极星量化终端，在实盘运行策略，支持K线触发、即时行情触发、交易数据触发、定时触发和周期性触发等方式
4. 实盘交易需要用户使用各自有效的期货交易账号，并在极星9.5上完成登录。

#### 安装教程
1. 安装Anaconda3
    a. 在浏览器打开https://repo.anaconda.com/archive/Anaconda3-5.2.0-Windows-x86_64.exe，下载Anaconda3
    b. 下载完成后，双击Anaconda3-5.2.0-Windows-x86_64.exe,全部选择下一步进行默认安装
    c. 在系统环境变量中加入Anaconda3安装路径及脚本路径，例如：C:\ProgramData\Anaconda3和C:\ProgramData\Anaconda3\Scripts
    
2. python依赖包安装
    a. 安装ta-lib库
        a1. 浏览器打开https://www.lfd.uci.edu/~gohlke/pythonlibs/，搜索TA-LIB，下载TA_Lib-0.4.17-cp36-cp36m-win_amd64.whl
        a2. Win+R运行cmd，进入TA_Lib的下载目录，执行pip install TA_Lib-0.4.17-cp36-cp36m-win_amd64.whl
        
    b. 安装tkcalendar,在cmd命令行窗口执行pip install tkcalendar安装
    
3. 极星量化下载
    a. 浏览器打开https://github.com/fanliangde/equant.git，单击Clone or download，选择Download ZIP下载或者使用sourcetree,githup desktop等git客户端下载
    b. 将极星量化安装包移动到任意目录，例如：D:\equant，并解压
    
4. 极星9.5客户端安装
    a. 浏览器打开https://epolestar95-1255628687.cos.ap-beijing.myqcloud.com/epolestar_0429.zip，下载极星9.5客户端
    b. 极星9.5客户端安装包移动到任意目录，例如:D\equant，并解压
    b. 打开9.5客户端主目录，找到equant.bat，右键编辑，修改equant-script.py所在的路径为极星量化的路径，例如D:\equant\equantV1.0

5. 安装注意事项
    a. Anaconda3安装过程中会自动安装Python3.6环境，如果已经有其他python环境，需要将Anaconda3安装的python3.6环境作为默认环境
    b. 默认Anaconda安装路径C:\ProgramData为隐藏目录，可在windows资源管理器地址栏上输入C:\ProgramData\Anaconda3确认目录是否存在

#### 使用说明
1. 打开极星9.5客户端，点击"量化"按钮，点击"Python"，打开极星量化终端，进行试用
2. 同一台机器上如果有多个9.5客户端，只能有一个客户端使用量化


#### 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request
