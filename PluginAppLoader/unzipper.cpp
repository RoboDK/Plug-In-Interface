#include "unzipper.h"

#include <QFile>

#include "zip.h"


static size_t callbackExtract(void* argument, uint64_t offset, const void *buffer, size_t size) {
    QFile* file = static_cast<QFile*>(argument);
    if (!file->seek(static_cast<qint64>(offset)))
        return 0;

    qint64 result = file->write(static_cast<const char*>(buffer), static_cast<qint64>(size));
    if (result < 0)
        return 0;

    return static_cast<size_t>(result);
}


Unzipper::Unzipper(const QString& fileName)
    : _fileName(fileName)
    , _zip(nullptr)
{
}

Unzipper::~Unzipper() {
    close();
}

bool Unzipper::open() {
    if (isOpen() || _fileName.isEmpty())
        return false;

    _zip = zip_open(_fileName.toUtf8().data(), 0, 'r');
    if (!_zip)
        return false;

    return true;
}

void Unzipper::close() {
    zip_close(_zip);
    _zip = nullptr;
}

bool Unzipper::selectEntry(quint32 index) {
    return (zip_entry_openbyindex(_zip, index) == 0);
}

quint32 Unzipper::entriesCount() const {
    ssize_t result = zip_entries_total(_zip);
    return (result < 0) ? 0 : static_cast<quint32>(result);
}

QString Unzipper::entryName() const {
    return QString::fromUtf8(zip_entry_name(_zip));
}

bool Unzipper::entryIsDirectory() const {
    return (zip_entry_isdir(_zip) == 1);
}

bool Unzipper::entryExtract(const QString& destination, bool overwrite) {
    QFile file(destination);

    if (entryIsDirectory())
        return false;

    if (!file.open(overwrite ? QFile::WriteOnly : QFile::NewOnly))
        return false;

    return (zip_entry_extract(_zip, &callbackExtract, &file) >= 0);
}

bool Unzipper::isOpen() const {
    return (_zip != nullptr);
}
