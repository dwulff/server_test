require(tidyverse)

fs = list.files("val", pattern = "*.csv", full.names = TRUE)

mods = lapply(fs, function(x){
  read_csv(x) |> mutate(model = x |> str_remove("val/") |> str_remove(".csv"))
  }) |> do.call(what = bind_rows)

p = mods |> 
  group_by(n_jobs, prompt_length, output_length_instruct, model) |> 
  summarize(n = n(), 
            sec = min(secs)) |> 
  ggplot(aes(x = as_factor(prompt_length), as_factor(output_length_instruct), fill = log(sec), label = round(sec, 1))) + 
  geom_tile() + 
  geom_text(col = "white") + 
  facet_grid(model~n_jobs) + 
  labs(x = "Prompt length (words)", y = "Output length (words)", 
       title = "Time per run (s)",
       subtitle = "by number of threads and model") + 
  guides(fill = "none", col = "none") + 
  scale_fill_viridis_c(option = "G", end = .8)

ggsave("eval_test.png", p, width = 12, height = length(fs) * 2.5, dpi = 300)