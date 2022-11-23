#ifndef APPLISTDELEGATE_H
#define APPLISTDELEGATE_H


#include <QIdentityProxyModel>
#include <QStyledItemDelegate>
#include <QScopedPointer>


class AppListProxyModel : public QIdentityProxyModel
{
    Q_OBJECT

public:
    QVariant data(const QModelIndex &proxyIndex, int role = Qt::DisplayRole) const override;
};

class AppListDelegate : public QStyledItemDelegate
{
    Q_OBJECT
public:
    explicit AppListDelegate(QObject* parent = nullptr);

    void paint(QPainter* painter, const QStyleOptionViewItem& option,
               const QModelIndex& index) const override;
    QSize sizeHint(const QStyleOptionViewItem& option,
                   const QModelIndex& index) const override;

private:
    QScopedPointer<AppListProxyModel> _proxy;
};


#endif // APPLISTDELEGATE_H
