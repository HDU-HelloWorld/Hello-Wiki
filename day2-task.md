# 总纲:Day2：负责 API 路由开发（Wiki API、版本 API、标签 API），并编写接口文档。


# api下新建的routes文件夹
apps/backend/src/api/routes


## wiki.py
apps/backend/src/api/routes/wiki.py
用于Wiki 页面 CRUD、目录树查询
新增路由函数：create_page, get_page, update_page, delete_page, get_tree

 ## versions.py
 apps/backend/src/api/routes/versions.py
 新增路由：get_versions, get_version_detail, compare_versions, rollback
版本管理 API

## tags.py
apps/backend/src/api/routes/tags.py
新增路由：get_all_tags, get_pages_by_t
标签 API



# 应用服务层


## wiki_application.py
apps/backend/src/application/wiki_application.py
WikiService 
业务逻辑
确认 Day1 已实现的方法：create_page, get_page, update_page, delete_page, get_page_tree 等。Day2 可能需要补充版本相关方法：get_page_versions, get_version_by_id, compare_versions, rollback_to_version

## tag_application.py
apps/backend/src/application/tag_application.py
标签服务
如果标签逻辑复杂，可以新建；简单情况下直接在路由层调用 repository