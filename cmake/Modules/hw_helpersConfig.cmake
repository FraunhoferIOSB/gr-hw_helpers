INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_HW_HELPERS hw_helpers)

FIND_PATH(
    HW_HELPERS_INCLUDE_DIRS
    NAMES hw_helpers/api.h
    HINTS $ENV{HW_HELPERS_DIR}/include
        ${PC_HW_HELPERS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    HW_HELPERS_LIBRARIES
    NAMES gnuradio-hw_helpers
    HINTS $ENV{HW_HELPERS_DIR}/lib
        ${PC_HW_HELPERS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(HW_HELPERS DEFAULT_MSG HW_HELPERS_LIBRARIES HW_HELPERS_INCLUDE_DIRS)
MARK_AS_ADVANCED(HW_HELPERS_LIBRARIES HW_HELPERS_INCLUDE_DIRS)

