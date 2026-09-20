% Учебный мир RPG. Все персонажи и связи вымышлены.
% 24 унарных факта: типы объектов, роли и состояние персонажа.
character(aria).
character(borin).
character(celia).
character(darin).
character(elin).
character(finn).
warrior(aria).
warrior(borin).
mage(celia).
healer(darin).
rogue(elin).
ranger(finn).
weapon(sword).
weapon(staff).
weapon(bow).
quest(ruins).
quest(forest).
quest(tower).
skill(melee).
skill(magic).
skill(tracking).
guild(sun).
guild(moon).
cursed(borin).

% 15 бинарных фактов: инвентарь, навыки, требования и гильдии.
owns(aria,sword).
owns(borin,sword).
owns(celia,staff).
owns(darin,staff).
owns(elin,bow).
owns(finn,bow).
has_skill(aria,melee).
has_skill(celia,magic).
has_skill(finn,tracking).
requires(ruins,melee).
requires(forest,tracking).
requires(tower,magic).
member_of(aria,sun).
member_of(celia,sun).
member_of(borin,moon).

% 7 правил. Режимы допускают поиск с переменными.
% Боец: воин или маг (дизъюнкция).
combatant(X) :- character(X), (warrior(X); mage(X)).
% Разведчик: разбойник или следопыт.
scout(X) :- character(X), (rogue(X); ranger(X)).
% Вооружённый персонаж имеет предмет типа weapon.
armed(X) :- character(X), owns(X,W), weapon(W).
% Навык персонажа совпадает с требованием задания.
skilled_for(X,Q) :- character(X), quest(Q), has_skill(X,S), requires(Q,S).
% Допуск по наличию оружия и подходящего навыка; не гарантия победы.
ready_for(X,Q) :- armed(X), skilled_for(X,Q).
% Разные персонажи состоят в одной гильдии.
guildmate(X,Y) :- character(X), character(Y), member_of(X,G), member_of(Y,G), dif(X,Y).
% Отрицание как неуспех: сначала перечисляем известных персонажей.
safe_character(X) :- character(X), \+ cursed(X).
