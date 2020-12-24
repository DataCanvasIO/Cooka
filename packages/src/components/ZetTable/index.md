---
title: ZetTable
subtitle: 表格
---

## API

ZetTable的属性说明如下：

属性 | 说明 | 类型 | 默认值
-----|-----|-----|------
tabledata | model中table的数据与参数 | object | -
columns | 表头 | array | 见下面附加内容
rowKey | key值绑定 | callback | record => record.id,
buttonlist | 左上功能按钮定义 | array | 见下面附加内容,
tableModelName | Table Model的Namespace | string | -

注: ZetTable 其它特性继承 Antd Table 组件

#### ZetTable专用Model模板

见组件目录或Example下的TABLE_MODEL_TEMPLATE.js.

*修改 TABLE_MODEL_NAME 为 model 的 namespace.非常重要 非常重要 非常重要*
API额外字段写在filters中或者自行处理。
修改筛选项或者其他filters下的字段，dispatch调用`changeFilter`，不需要请求数据，默认会自动刷新。
示例如下：
```
changeType = ({ key }) => {
  const { dispatch } = this.props;
  dispatch({
    type: 'tagtable/changeFilter',
    payload: {
      type: 'typeId',
      value: key,
    },
  });
}
```
请求数据调用`queryTable`。
请求第一页数据使用`queryTableFirstPage`。

#### columns

格式参照antd.

Example:
```
[
  {
    title: '序号',
    width: 100,
    render: (text, record, index) => (
      index + 1
    ),
  },
  {
    title: '标签',
    dataIndex: 'name',
    sorter: true,
    width: '20%',
  },
  {
    title: '所属类型',
    dataIndex: 'typeId',
    filters: [{
      text: '分析模块',
      value: '0',
    }, {
      text: '数据集',
      value: '1',
    }],
    filterMultiple: false,
    width: '20%',
    render: (text) => {
      switch (text) {
        case 0: return '分析模块';
        case 1: return '数据集';
        case 2: return '工作流';
        case 3: return '项目管理';
        default: return '';
      }
    },
  },
  {
    title: '操作',
    render: (record) => (
      <Popconfirm
        title="确定要删除这个标签吗"
        onConfirm={() => { this.deleteTag(record.id); }}
        okText="删除"
        cancelText="取消"
      >
        <a>删除</a>
      </Popconfirm>
    ),
  },
]
```

#### buttionlist

属性 | 说明 | 类型 | 默认值
-----|-----|-----|------
name | 显示名字 | string | -
type | 显示样式 | string | 见Antd Button文档
callback | 功能回调 | function(selectedRowKeys, selectedRows) | -
props | 其他Props属性 | object | -

```
[
  { name: '测试1', callback: () => {}, props: { disabled: true } },
  { name: '测试2', type: 'primary', callback: (a, b) => { console.log(a, b); } },
  { name: '测试3', type: 'dashed', callback: () => {} },
  { name: '测试4', type: 'danger', callback: () => {} },
]
```

#### Example

见Example
