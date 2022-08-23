#ifndef UNZIPPER_H
#define UNZIPPER_H


#include <QString>


struct zip_t;


class Unzipper
{
public:
    Unzipper(const QString &fileName);
    ~Unzipper();

    bool open();
    void close();

    bool selectEntry(quint32 index);

    quint32 entriesCount() const;
    QString entryName() const;
    bool entryIsDirectory() const;
    bool entryExtract(const QString& destination, bool overwrite = true);

    bool isOpen() const;

private:
    QString _fileName;

    zip_t* _zip;
};

#endif // UNZIPPER_H
