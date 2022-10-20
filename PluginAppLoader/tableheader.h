#ifndef TABLEHEADER_H
#define TABLEHEADER_H


#include <QHeaderView>
#include <QMouseEvent>


class TableHeader : public QHeaderView
{
    Q_OBJECT

public:
    TableHeader(Qt::Orientation orientation, QWidget* parent = nullptr):
        QHeaderView(orientation, parent){
        setSectionsClickable(true);
    }

protected:
    virtual void mousePressEvent(QMouseEvent *e){
        int index = logicalIndexAt(e->pos());

        bool clickable = sectionsClickable();

        if (index == 3 || index == 6)
            setSectionsClickable(false);

        QHeaderView::mousePressEvent(e);

        setSectionsClickable(clickable);
    }

    virtual void mouseReleaseEvent(QMouseEvent *e){
        int index = logicalIndexAt(e->pos());

        bool clickable = sectionsClickable();

        if (index == 3 || index == 6)
            setSectionsClickable(false);

        QHeaderView::mouseReleaseEvent(e);

        setSectionsClickable(clickable);
    }
};


#endif // TABLEHEADER_H
