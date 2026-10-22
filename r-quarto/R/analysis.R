# Statistical helpers for the penguins report. Mirrors python/src/penguin_lab/analysis.py.

NUMERIC <- c("bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g")

#' Read the CSV and keep complete cases (the 4 measurements and sex).
load_penguins <- function(path = file.path("..", "data", "penguins.csv")) {
  df <- readr::read_csv(path, na = "NA", show_col_types = FALSE)
  df[stats::complete.cases(df[, c(NUMERIC, "sex")]), ]
}

#' Count, mean and sample standard deviation of each measurement per species.
species_summary <- function(df) {
  df |>
    dplyr::group_by(species) |>
    dplyr::summarise(
      n = dplyr::n(),
      dplyr::across(
        dplyr::all_of(NUMERIC),
        list(mean = mean, sd = stats::sd),
        .names = "{.col}_{.fn}"
      ),
      .groups = "drop"
    )
}

#' Welch two-sample t-test (R's default `t.test`) between two species.
welch_test <- function(df, a, b, column = "flipper_length_mm") {
  x <- df[[column]][df$species == a]
  y <- df[[column]][df$species == b]
  res <- stats::t.test(x, y, var.equal = FALSE)
  list(
    t = unname(res$statistic),
    df = unname(res$parameter),
    p_value = res$p.value,
    mean_diff = mean(x) - mean(y)
  )
}

#' Ordinary least squares: body_mass_g ~ flipper_length_mm.
mass_on_flipper <- function(df) {
  fit <- stats::lm(body_mass_g ~ flipper_length_mm, data = df)
  list(
    slope = unname(stats::coef(fit)[2]),
    intercept = unname(stats::coef(fit)[1]),
    r_squared = summary(fit)$r.squared,
    n = nrow(df)
  )
}

#' Scatter plot of flipper length vs body mass, one colour per species.
plot_flipper_mass <- function(df) {
  ggplot2::ggplot(df, ggplot2::aes(flipper_length_mm, body_mass_g, colour = species)) +
    ggplot2::geom_point(alpha = 0.8, size = 1.8) +
    ggplot2::geom_smooth(
      ggplot2::aes(group = 1), method = "lm", formula = y ~ x,
      colour = "grey25", linewidth = 0.7, se = TRUE
    ) +
    ggplot2::scale_colour_manual(values = c(Adelie = "#c2410c", Chinstrap = "#6d28d9", Gentoo = "#0e7490")) +
    ggplot2::labs(
      x = "Flipper length (mm)", y = "Body mass (g)", colour = "Species",
      title = "Heavier penguins have longer flippers",
      caption = "Data: Palmer Station LTER, CC0 (Gorman et al. 2014)"
    ) +
    ggplot2::theme_minimal(base_size = 12)
}
