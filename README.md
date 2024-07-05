<h1 align="center">iirosebot-plugins</h1>

<p align="center">一个用于存放 <a href="https://github.com/XCWQW1/iirosebot">iirosebot</a> 框架插件的仓库</p>
<p align="center"><a href="https://github.com/XCWQW1/iirosebot-plugins/blob/main/data/README.md"><strong>插件列表</strong></a></p>

> 使用前请仔细查阅该插件的README 

如果您想提交您的插件到本仓库，请fork [示例仓库](https://github.com/XCWQW1/iirose_example) 按格式修改后修改本仓库列表并且pr

#### iirosebot版本小于1.7.0的插件迁移教程：将所有与框架有关的import\from前面加上```iirosebot.```
#### 例：
```python
from API.api_iirose import APIIirose
```
#### 改为
```python
from iirosebot.API.api_iirose import APIIirose
```
