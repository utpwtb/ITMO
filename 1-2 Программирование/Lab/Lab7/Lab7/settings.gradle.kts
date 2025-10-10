rootProject.name = "template"

include(":client")
include(":common")
include(":server")

project(":client").projectDir = file("src/client")
project(":common").projectDir = file("src/common")
project(":server").projectDir = file("src/server")