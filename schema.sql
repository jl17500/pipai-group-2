-- Scent Optimizer feature rankings (Google Form export).
-- Rank 1 is the respondent's top feature. Re-running is safe.

create table if not exists feature_rankings (
  id bigint generated always as identity primary key,
  submitted_at timestamp not null,
  respondent_name text not null,
  user_type text not null,
  rank_initial_survey smallint not null check (rank_initial_survey between 1 and 8),
  rank_rating_feature smallint not null check (rank_rating_feature between 1 and 8),
  rank_top_5_for_you smallint not null check (rank_top_5_for_you between 1 and 8),
  rank_meta_score_and_explanation smallint not null check (rank_meta_score_and_explanation between 1 and 8),
  rank_friend_score smallint not null check (rank_friend_score between 1 and 8),
  rank_scent_lookup smallint not null check (rank_scent_lookup between 1 and 8),
  rank_not_for_me_button smallint not null check (rank_not_for_me_button between 1 and 8),
  rank_dupe_finder smallint not null check (rank_dupe_finder between 1 and 8),
  feedback text,
  unique (submitted_at, respondent_name)
);

insert into feature_rankings (
  submitted_at,
  respondent_name,
  user_type,
  rank_initial_survey,
  rank_rating_feature,
  rank_top_5_for_you,
  rank_meta_score_and_explanation,
  rank_friend_score,
  rank_scent_lookup,
  rank_not_for_me_button,
  rank_dupe_finder,
  feedback
) values
  ('2026-10-06 18:45:10', 'Frank', 'Fragrance enthusiast / collector', 3, 2, 7, 8, 1, 6, 5, 4, null),
  ('2026-10-06 18:49:01', 'Shrishti', 'Online shopper avoiding blind-buy mistakes', 3, 1, 2, 5, 6, 8, 4, 7, null),
  ('2026-10-06 18:49:11', 'Sterling McIver-Heyward', 'Budget-conscious scent shopper', 1, 4, 3, 6, 8, 2, 5, 7, 'Yes'),
  ('2026-10-06 18:50:12', 'Ananya', 'Occasional fragrance buyer', 5, 6, 2, 1, 8, 3, 4, 7, null)
on conflict (submitted_at, respondent_name) do nothing;
