-- Blind scent ratings (scent_ratings.csv).
-- 1 Hate, 2 Dislike, 3 Like, 4 Love. Re-running is safe.

create table if not exists scent_ratings (
  id bigint generated always as identity primary key,
  person text not null,
  category text not null,
  item_number smallint not null check (item_number > 0),
  item_label text not null,
  brand text,
  product_name text,
  rating smallint not null,
  rating_label text not null,
  check (
    (rating = 1 and rating_label = 'Hate')
    or (rating = 2 and rating_label = 'Dislike')
    or (rating = 3 and rating_label = 'Like')
    or (rating = 4 and rating_label = 'Love')
  ),
  unique (person, category, item_number)
);

insert into scent_ratings (
  person,
  category,
  item_number,
  item_label,
  brand,
  product_name,
  rating,
  rating_label
) values
  ('Layla', 'Perfume', 1, 'Perfume 1', null, null, 2, 'Dislike'),
  ('Layla', 'Candle', 1, 'Candle 1', null, null, 3, 'Like'),
  ('Layla', 'Deodorant', 1, 'Deodorant 1', null, null, 3, 'Like'),
  ('Jerry', 'Perfume', 1, 'Perfume 1', null, null, 2, 'Dislike'),
  ('Jerry', 'Candle', 1, 'Candle 1', null, null, 3, 'Like'),
  ('Jerry', 'Deodorant', 1, 'Deodorant 1', null, null, 3, 'Like'),
  ('Bruno', 'Perfume', 1, 'Perfume 1', null, null, 2, 'Dislike'),
  ('Bruno', 'Candle', 1, 'Candle 1', null, null, 2, 'Dislike'),
  ('Bruno', 'Deodorant', 1, 'Deodorant 1', null, null, 3, 'Like'),
  ('Owen', 'Perfume', 1, 'Perfume 1', null, null, 2, 'Dislike'),
  ('Owen', 'Candle', 1, 'Candle 1', null, null, 4, 'Love'),
  ('Owen', 'Deodorant', 1, 'Deodorant 1', null, null, 3, 'Like'),
  ('Owen', 'Body wash', 1, 'Body wash 1', null, null, 1, 'Hate'),
  ('Owen', 'Lotion', 1, 'Lotion 1', null, null, 3, 'Like'),
  ('Owen', 'Lotion', 2, 'Lotion 2', null, null, 2, 'Dislike'),
  ('Owen', 'Shampoo', 1, 'Shampoo 1', null, null, 3, 'Like'),
  ('Owen', 'Perfume', 2, 'Perfume 2', null, null, 2, 'Dislike'),
  ('Owen', 'Perfume', 3, 'Perfume 3', null, null, 3, 'Like'),
  ('Owen', 'Candle', 2, 'Candle 2', null, null, 1, 'Hate'),
  ('Owen', 'Candle', 3, 'Candle 3', null, null, 1, 'Hate'),
  ('Jing', 'Candle', 1, 'Candle 1', null, null, 3, 'Like'),
  ('Jing', 'Perfume', 1, 'Perfume 1', null, null, 2, 'Dislike'),
  ('Jing', 'Deodorant', 1, 'Deodorant 1', null, null, 2, 'Dislike'),
  ('Jing', 'Body wash', 1, 'Body wash 1', null, null, 2, 'Dislike'),
  ('Jing', 'Lotion', 1, 'Lotion 1', null, null, 3, 'Like'),
  ('Jing', 'Lotion', 2, 'Lotion 2', null, null, 4, 'Love'),
  ('Jing', 'Shampoo', 1, 'Shampoo 1', null, null, 3, 'Like'),
  ('Jing', 'Perfume', 2, 'Perfume 2', null, null, 1, 'Hate'),
  ('Jing', 'Perfume', 3, 'Perfume 3', null, null, 2, 'Dislike'),
  ('Jing', 'Candle', 2, 'Candle 2', null, null, 2, 'Dislike'),
  ('Jing', 'Candle', 3, 'Candle 3', null, null, 2, 'Dislike'),
  ('Paul', 'Candle', 1, 'Candle 1', null, null, 2, 'Dislike'),
  ('Paul', 'Perfume', 1, 'Perfume 1', null, null, 2, 'Dislike'),
  ('Paul', 'Deodorant', 1, 'Deodorant 1', null, null, 3, 'Like'),
  ('Paul', 'Shampoo', 1, 'Shampoo 1', 'Native', 'Coconut Vanilla', 2, 'Dislike'),
  ('Paul', 'Lotion', 1, 'Lotion 1', 'Athena', 'Amber Hours', 3, 'Like'),
  ('Paul', 'Lotion', 2, 'Lotion 2', 'Athena', 'Golden Vanilla', 4, 'Love'),
  ('Paul', 'Shampoo', 2, 'Shampoo 2', 'Native', 'Rain + Cashmere', 3, 'Like'),
  ('Paul', 'Perfume', 2, 'Perfume 2', null, null, 1, 'Hate'),
  ('Paul', 'Perfume', 3, 'Perfume 3', null, null, 3, 'Like'),
  ('Paul', 'Candle', 2, 'Candle 2', null, null, 2, 'Dislike'),
  ('Paul', 'Candle', 3, 'Candle 3', null, null, 2, 'Dislike')
on conflict (person, category, item_number) do nothing;
