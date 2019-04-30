# 极星量化终端

#### 介绍
1. 极星量化终端基于python开发，结合极星9.5PC版使用，运行在Windows7及系统以上x64平台上
2. 量化交易者可使用极星量化终端编写策略、加载策略进行回测，并根据回测报告掌握策略盈亏情况。
3. 量化交易者可使用极星量化终端，在实盘运行策略，支持K线触发、即时行情触发、交易数据触发、定时触发和周期性触发等方式
4. 实盘交易需要用户使用各自有效的期货交易账号，并在极星9.5上完成登录。

#### 安装教程
1. 安装极星9.5客户端  
    a. 单击[极星9.5客户端](https://epolestar95-1255628687.cos.ap-beijing.myqcloud.com/epolestar_0429.zip)，下载极星9.5客户端  
    b. 极星9.5客户端安装包移动到任意目录，例如:D\equant，并解压  

2. 安装Anaconda3  
    a. 打开[Anaconda官网](https://www.anaconda.com)下载最新python3.7 Anaconda3版本   
    b. 双击安装文件，点击"Next",出现"Add Anaconda3 to the system PATH environment variable"时勾选,其他点击"Next"  
    
3. 安装python依赖包 
    a. 安装talib库  
        a1. 打开[talib下载地址](https://www.lfd.uci.edu/~gohlke/pythonlibs/)，搜索TA-LIB，下载TA_Lib-0.4.17-cp36-cp36m-win_amd64.whl   
        a2. Win+R运行cmd，进入TA_Lib的下载目录，执行pip install TA_Lib-0.4.17-cp36-cp36m-win_amd64.whl  
    
4. 安装极星量化     
    a. 在gitee或者github，极星量化项目，单击Clone or download下载极星量化终端  
    b. 将极星量化终端安装包移动到任意目录，例如：D:\equant，并解压  
    c. 打开9.5客户端主目录，找到equant.bat，右键编辑，修改equant-script.py所在的路径为极星量化的路径，例如D:\equant\equantV1.0  

#### 使用说明
1. 打开极星9.5客户端，点击"量化"按钮，点击"Python"，打开极星量化终端，进行试用
2. 同一台机器上如果有多个9.5客户端，只能有一个客户端使用量化


#### 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request
