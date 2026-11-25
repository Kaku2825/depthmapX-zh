// Copyright (C) 2011-2012, Tasos Varoudis
// Copyright (C) 2017 Christian Sailer

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include <QPixmap>
#include <QDir>
#include <QDateTime>
#include <QFileInfo>
#include <QLibraryInfo>
#include <QTranslator>

#include "coreapplication.h"

#ifdef _WIN32
#include <windows.h>
#endif

// ---------------------------------------------------------------------------
// 中文界面支持（本项目相对上游的改动）
//
// 上游 depthmapX 的界面文案全部用 tr() 包裹，但从入口到主窗口都没有安装
// QTranslator，因此官方发行包无法显示中文。这里在应用启动时加载两份翻译：
//   1. Qt 自带的 qt_zh_CN —— 文件对话框、标准按钮等框架文案；
//   2. 本项目的 depthmapX_zh_CN.qm —— depthmapX 自身的菜单与对话框。
//
// 翻译文件放在 exe 同级或 exe 同级的 translations/ 目录下，存在即启用。
// 想恢复英文界面：删除 depthmapX_zh_CN.qm，或设置环境变量 DEPTHMAPX_LANG=en。
// ---------------------------------------------------------------------------
static void installChineseTranslators(QCoreApplication &app)
{
    if (qgetenv("DEPTHMAPX_LANG").toLower() == "en") {
        return;
    }

    auto *qtTranslator = new QTranslator(&app);
    if (qtTranslator->load(QStringLiteral("qt_zh_CN"),
                           QLibraryInfo::location(QLibraryInfo::TranslationsPath))) {
        app.installTranslator(qtTranslator);
    }

    auto *appTranslator = new QTranslator(&app);
    const QString appDir = QCoreApplication::applicationDirPath();
    const QStringList candidates = {
        appDir + QStringLiteral("/translations/depthmapX_zh_CN.qm"),
        appDir + QStringLiteral("/depthmapX_zh_CN.qm"),
        QStringLiteral(":/translations/depthmapX_zh_CN.qm")};
    for (const QString &path : candidates) {
        if (path.startsWith(QLatin1Char(':')) || QFileInfo::exists(path)) {
            if (appTranslator->load(path)) {
                app.installTranslator(appTranslator);
                break;
            }
        }
    }
}


int main(int argc, char *argv[])
{
    Q_INIT_RESOURCE(resource);
    Q_INIT_RESOURCE(settingsdialog);

    CoreApplication app(argc, argv);
    installChineseTranslators(app);

    return app.exec();
}
