library(testthat)
source(file.path("R", "analysis.R"))
test_dir("tests/testthat", reporter = "summary", stop_on_failure = TRUE)
