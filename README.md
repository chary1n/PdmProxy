# PdmProxy
PdmProxy
打包流程记录
1.首先将python代码打包成windows可执行文件(exe)
cmd: python setup1.py py2exe

2.将exe以及其他依赖文件打包成一个exe安装包

3.下载Inno Setup软件  双击打开setup_0410中文.iss

4.图标制作：网上下载下来的图标可能不能使用， 需要用Greenfish Icon Editor Pro生成后 即可出现


Mac 打包 流程记录
1.sudo python setup.py py2app
2.dist 复制文件夹中的.app文件. 直接使用 或者打包成dmg 使用...