create table
  public.resources (
    id bigint generated by default as identity,
    red_ml integer null default 0,
    green_ml integer null default 0,
    blue_ml integer null default 0,
    constraint potion_ml_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.potion_stock (
    id bigint generated by default as identity,
    red integer null,
    green integer null,
    blue integer null,
    dark integer null,
    name text null,
    sku text null,
    price text null,
    quantity integer null,
    type integer[] null,
    constraint potion_count_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.extra_resources (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    gold integer null,
    dark_ml integer null,
    constraint extra_resources_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.carts_and_items (
    id integer generated by default as identity,
    quantity integer null,
    sku text null,
    constraint carts_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.carts_and_customers (
    id bigint generated by default as identity,
    name text null,
    class text null,
    level integer null,
    constraint carts_and_customers_pkey primary key (id)
  ) tablespace pg_default;