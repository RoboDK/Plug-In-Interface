#include "applistdelegate.h"

#include <QDebug>


QVariant AppListProxyModel::data(const QModelIndex& proxyIndex, int role) const
{
    if (role == Qt::DisplayRole)
    {
        QVariant var = QIdentityProxyModel::data(proxyIndex, Qt::UserRole);
        if (!var.isNull())
            return var;
    }

    return QIdentityProxyModel::data(proxyIndex, role);
}

AppListDelegate::AppListDelegate(QObject* parent)
    : QStyledItemDelegate(parent)
    , _proxy(new AppListProxyModel())
{
}

void AppListDelegate::paint(QPainter* painter, const QStyleOptionViewItem& option, const QModelIndex& index) const
{
    if (_proxy->sourceModel() != index.model())
        _proxy->setSourceModel(const_cast<QAbstractItemModel*>(index.model()));

    QStyledItemDelegate::paint(painter, option, _proxy->mapFromSource(index));
}

QSize AppListDelegate::sizeHint(const QStyleOptionViewItem& option, const QModelIndex& index) const
{
    if (_proxy->sourceModel() != index.model())
        _proxy->setSourceModel(const_cast<QAbstractItemModel*>(index.model()));

    QSize hint = QStyledItemDelegate::sizeHint(option, _proxy->mapFromSource(index));
    if (index.column() == 0 && hint.width() < 100)
        hint.setWidth(100);

    return hint;
}
