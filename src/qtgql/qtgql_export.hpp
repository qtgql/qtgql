#pragma once
#include <QtCore/QtGlobal>

#if defined(QTGQL_CORE_LIB_SHARED_BUILD)
#define QTGQL_EXPORT Q_DECL_EXPORT
#else
#define QTGQL_EXPORT Q_DECL_IMPORT
#endif
