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

#ifndef ROBODK_STATIONTREEEVENTMONITOR_H
#define ROBODK_STATIONTREEEVENTMONITOR_H

#include <cstdint>
#include <unordered_map>
#include <functional>

#include <QObject>
#include <QVector>
#include <QHash>


class QIcon;
class QModelIndex;
class QTreeWidget;
class QTreeWidgetItem;
class IRoboDK;
class IItem;


namespace robodk
{

class StationTreeEventMonitor : public QObject
{
    Q_OBJECT

public:
    enum Filter : uint32_t
    {
        NoFilter               = 0x00000000,
        IgnoreInactiveStations = 0x00000001,
        IgnoreNameChange       = 0x00000002,
        IgnoreIconChange       = 0x00000004,
        IgnoreAdd              = 0x00000008,
        IgnoreRemove           = 0x00000010,
        IgnoreChildren         = 0x00000020,
    };

public:
    explicit StationTreeEventMonitor(IRoboDK* rdk, QObject* parent = nullptr);

    void setFilter(uint32_t filter);

    void test();

signals:
    void itemNameChanged(IItem* item, const QString& name);
    void itemIconChanged(IItem* item, const QIcon& icon);
    void itemAdded(IItem* item);
    void itemRemoved(IItem* item);

public slots:
    void refresh();

private slots:
    void onModelDataChanged(
        const QModelIndex& topLeft,
        const QModelIndex& bottomRight,
        const QVector<int>& roles = QVector<int>());
    void onModelRowsInserted(const QModelIndex& parent, int first, int last);
    void onModelRowsRemoved(const QModelIndex& parent, int first, int last);

private:
    struct QStringHash
    {
        inline size_t operator()(const QString& s) const { return qHash(s); };
    };

    using TreeCallback = std::function<void(const QModelIndex&)>;

private:
    void iterateOverTree(
        const QModelIndex& parent,
        const TreeCallback& callback,
        bool reverse = false);
    IItem* itemFromIndex(const QModelIndex& index) const;
    bool isActiveStationItem(const QModelIndex& index) const;

private:
    IRoboDK* _rdk = nullptr;
    QTreeWidget* _tree = nullptr;

    uint32_t _filter = IgnoreInactiveStations;

    std::unordered_multimap<QString, IItem*, QStringHash> _nameTable;
    std::unordered_map<IItem*, QString> _nameCache;
};


inline void StationTreeEventMonitor::setFilter(uint32_t filter)
{
    _filter = filter;
}

} // namespace robodk

#endif // STATIONTREEEVENTMONITOR_H
