csv <- file.path("..", "..", "..", "data", "penguins.csv")
expected <- jsonlite::read_json(file.path("..", "..", "..", "data", "expected_stats.json"))
df <- load_penguins(csv)

test_that("complete cases match the Python implementation", {
  expect_equal(nrow(df), expected$n_complete)
  expect_false(anyNA(df[, c(NUMERIC, "sex")]))
})

test_that("species counts are 146 / 68 / 119", {
  s <- species_summary(df)
  expect_equal(setNames(s$n, s$species), c(Adelie = 146, Chinstrap = 68, Gentoo = 119))
})

test_that("Welch t-test reproduces the Python numbers", {
  e <- expected$welch_flipper_adelie_gentoo
  r <- welch_test(df, "Adelie", "Gentoo")
  expect_equal(r$t, e$t, tolerance = 1e-8)
  expect_equal(r$df, e$df, tolerance = 1e-8)
  expect_equal(r$mean_diff, e$mean_diff, tolerance = 1e-8)
  expect_lt(r$p_value, 1e-50)
})

test_that("OLS reproduces the Python numbers", {
  e <- expected$ols_mass_on_flipper
  r <- mass_on_flipper(df)
  expect_equal(r$slope, e$slope, tolerance = 1e-8)
  expect_equal(r$intercept, e$intercept, tolerance = 1e-8)
  expect_equal(r$r_squared, e$r_squared, tolerance = 1e-8)
})

test_that("the plot builds without error", {
  expect_s3_class(plot_flipper_mass(df), "ggplot")
})
