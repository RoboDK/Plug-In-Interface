/****************************************************************************
**
** Copyright (c) 2015-2025 RoboDK Inc.
** Contact: https://robodk.com/
**
** This file is part of the RoboDK API.
**
** Permission is hereby granted, free of charge, to any person obtaining a copy
** of this software and associated documentation files (the "Software"), to deal
** in the Software without restriction, including without limitation the rights
** to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
** copies of the Software, and to permit persons to whom the Software is
** furnished to do so, subject to the following conditions:
**
** The above copyright notice and this permission notice shall be included in all
** copies or substantial portions of the Software.
**
** THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
** IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
** FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
** AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
** LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
** OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
** SOFTWARE.
**
** RoboDK is a registered trademark of RoboDK Inc.
**
****************************************************************************/

#include "stationtreeeventmonitor.h"

#include <stack>

#include <QTreeWidget>
#include <QTreeWidgetItem>
#include <QDebug>
#include <QTimer>

#include "iitem.h"


namespace robodk
{

StationTreeEventMonitor::StationTreeEventMonitor(IRoboDK* rdk, QObject* parent)
    : QObject(parent)
    , _rdk(rdk)
{
    if (!_rdk)
        return;

    const auto items = _rdk->getItemList();
    for (const auto& item : items)
    {
        auto treeItem = dynamic_cast<QTreeWidgetItem*>(item);
        if (treeItem && treeItem->treeWidget())
        {
            _tree = treeItem->treeWidget();
            break;
        }
    }

    if (!_tree)
        return;

    auto model = _tree->model();

    using ModelClass = QAbstractItemModel;
    using ThisClass = StationTreeEventMonitor;
    connect(model, &ModelClass::modelReset, this, &ThisClass::refresh);
    connect(model, &ModelClass::dataChanged, this, &ThisClass::onModelDataChanged);
    connect(model, &ModelClass::rowsInserted, this, &ThisClass::onModelRowsInserted);
    connect(model, &ModelClass::rowsRemoved, this, &ThisClass::onModelRowsRemoved);

    refresh();
}

void StationTreeEventMonitor::refresh()
{
    _nameTable.clear();
    _nameCache.clear();

    if (!_tree || !_tree->model())
        return;

    iterateOverTree(QModelIndex(), [this] (const QModelIndex& index)
    {
        auto item = itemFromIndex(index);
        if (!item)
            return;

        const QString name = index.data().toString();
        _nameTable.insert({name, item});
        _nameCache[item] = name;
    });
}

void StationTreeEventMonitor::submit()
{
    bool child = false;

    auto addItem = [this, &child] (const QModelIndex& index)
    {
        auto item = itemFromIndex(index);
        if (!item)
            return;

        const QString name = index.data().toString();
        _nameTable.insert({name, item});
        _nameCache[item] = name;

        if (_filter & IgnoreAdd)
            return;

        if ((_filter & IgnoreChildren) && child)
            return;

        if ((_filter & IgnoreInactiveStations) && !isActiveStationItem(index))
            return;

        emit itemAdded(item);
    };

    for (const auto& index : _addedIndices)
    {
        child = false;
        addItem(index);

        child = true;
        iterateOverTree(index, addItem);
    }

    _addedIndices.clear();
}

void StationTreeEventMonitor::onModelDataChanged(
    const QModelIndex& topLeft,
    const QModelIndex& bottomRight,
    const QVector<int>& roles)
{
    if (!topLeft.isValid() || !bottomRight.isValid() || topLeft.parent() != bottomRight.parent())
        return;

    bool nameChanged = false;
    bool iconChanged = false;

    for (int role : roles)
    {
        switch (role)
        {
        case Qt::DisplayRole:
        case Qt::EditRole:
            nameChanged = true;
            break;
        case Qt::DecorationRole:
            iconChanged = true;
            break;
        default:
            break;
        }
    }

    bool isActive = (_filter & IgnoreInactiveStations) == 0 || isActiveStationItem(topLeft);
    const auto parent = topLeft.parent();

    auto updateItem = [this, nameChanged, iconChanged, isActive, parent] (const QModelIndex& index)
    {
        auto item = itemFromIndex(index);
        if (!item)
            return;

        const auto cache = _nameCache.find(item);
        if (cache == _nameCache.end())
            return;

        const auto range = _nameTable.equal_range(cache->second);
        for (auto it = range.first; it != range.second; ++it)
        {
            if (it->second == item)
            {
                _nameTable.erase(it);
                break;
            }
        }

        const QString name = index.data().toString();
        _nameTable.insert({name, item});
        _nameCache[item] = name;

        if (!isActive)
            return;

        if ((_filter & IgnoreChildren) && parent != index.parent())
            return;

        if (nameChanged && (_filter & IgnoreNameChange) == 0)
            emit itemNameChanged(item, name);

        if (iconChanged && (_filter & IgnoreIconChange) == 0)
            emit itemIconChanged(item, qvariant_cast<QIcon>(index.data(Qt::DecorationRole)));
    };

    for (int row = topLeft.row(); row <= bottomRight.row(); ++row)
    {
        auto index = _tree->model()->index(row, 0, topLeft.parent());
        if (!index.isValid())
            continue;

        updateItem(index);
        iterateOverTree(index, updateItem);
    }
}

void StationTreeEventMonitor::onModelRowsInserted(const QModelIndex& parent, int first, int last)
{
    for (int row = first; row <= last; ++row)
    {
        auto index = _tree->model()->index(row, 0, parent);
        if (index.isValid())
            _addedIndices.push_back(index);
    }

    if (_policy == AutoSubmit)
        QTimer::singleShot(0, this, &StationTreeEventMonitor::submit);
}

void StationTreeEventMonitor::onModelRowsRemoved(const QModelIndex& parent, int first, int last)
{
    auto removeItem = [this, &parent] (const QModelIndex& index)
    {
        auto item = itemFromIndex(index);
        if (!item)
            return;

        const auto cache = _nameCache.find(item);
        if (cache == _nameCache.end())
            return;

        const auto range = _nameTable.equal_range(cache->second);
        for (auto it = range.first; it != range.second; ++it)
        {
            if (it->second == item)
            {
                _nameTable.erase(it);
                break;
            }
        }

        _nameCache.erase(cache);

        if (_filter & IgnoreRemove)
            return;

        if ((_filter & IgnoreChildren) && parent != index.parent())
            return;

        if ((_filter & IgnoreInactiveStations) && !isActiveStationItem(index))
            return;

        emit itemRemoved(item);
    };

    for (int row = last; row >= first; --row)
    {
        auto index = _tree->model()->index(row, 0, parent);
        if (!index.isValid())
            continue;

        iterateOverTree(index, removeItem, true);
        removeItem(index);
    }
}

void StationTreeEventMonitor::iterateOverTree(
    const QModelIndex& parent,
    const TreeCallback& callback,
    bool reverse)
{
    auto model = _tree->model();

    using StackEntry = std::pair<int, QModelIndex>;
    std::stack<StackEntry> stack;
    stack.push({0, parent});

    while (!stack.empty())
    {
        auto& entry = stack.top();
        const auto& parent = entry.second;
        const int start = entry.first;
        const int count = model->rowCount(parent);

        bool goBack = true;

        if (reverse && start > 0)
        {
            auto index = model->index(count - start, 0, parent);
            callback(index);
        }

        for (int i = start; i < count; ++i)
        {
            int row = reverse ? (count - i - 1) : i;

            auto index = model->index(row, 0, parent);
            if (!index.isValid())
                continue;

            if (!reverse)
                callback(index);

            if (model->hasChildren(index))
            {
                entry.first = i + 1;
                stack.push({0, index});
                goBack = false;
                break;
            }
            else if (reverse)
            {
                callback(index);
            }
        }

        if (goBack)
            stack.pop();
    }
}

IItem* StationTreeEventMonitor::itemFromIndex(const QModelIndex& index) const
{
    auto treeItem = static_cast<QTreeWidgetItem*>(index.internalPointer());
    return dynamic_cast<IItem*>(treeItem);
}

bool StationTreeEventMonitor::isActiveStationItem(const QModelIndex& index) const
{
    QModelIndex parent = index;
    while (parent.parent().isValid())
        parent = parent.parent();

    if (!parent.isValid())
        return false;

    auto item = itemFromIndex(parent);
    return item && _rdk && item == _rdk->getActiveStation();
}

} // namespace robodk
