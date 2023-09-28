--query 1
CREATE VIEW buying_by_sector AS(
    SELECT distinct Buying.tDate, Buying.ID, Sector
    FROM Buying INNER JOIN Company ON Buying.Symbol=Company.Symbol
);

CREATE VIEW buyer_sector_counter_per_day AS(
    SELECT tDate, ID, COUNT(Sector) as sector_counter
    FROM buying_by_sector
    GROUP BY tDate,ID
    HAVING COUNT(sector)>=8
);

CREATE VIEW name_and_id_diverse_investor AS(
    SELECT distinct buyer_sector_counter_per_day.ID, Investor.Name
    FROM buyer_sector_counter_per_day INNER JOIN Investor ON Investor.ID=buyer_sector_counter_per_day.ID
);

CREATE VIEW diverse_investor_amount_spent_per_date AS(
    SELECT Buying.ID,Name, BQuantity*Price AS paid_per_date
    FROM (Buying INNER JOIN name_and_id_diverse_investor ON Buying.ID=name_and_id_diverse_investor.ID)
        INNER JOIN Stock ON (Buying.Symbol=Stock.Symbol AND Stock.tDate=Buying.tDate)
);

--query 2
CREATE VIEW all_Dates
AS
SELECT distinct tDate
FROM Buying;

CREATE VIEW days_amount
AS
SELECT count(*) as amount_of_days
FROM all_Dates;


CREATE VIEW companies_distinct_days
AS
SELECT DISTINCT tDate, symbol
FROM Buying;


CREATE VIEW popular_companies
AS
SELECT Symbol, Count(tDate) AS counter
FROM companies_distinct_days, days_amount
GROUP BY Symbol, amount_of_days
HAVING Count(tDate) > (amount_of_days)/2;


CREATE VIEW id_company_stock_amount
AS
SELECT ID, Symbol, sum(bquantity) as sumBq
FROM Buying
GROUP BY ID, Symbol
HAVING sum(BQuantity)>10;


CREATE VIEW people_bought_popular_companies_stock
AS
SELECT id_company_stock_amount.ID, popular_companies.SYMBOL, sumBq, investor.name
FROM id_company_stock_amount, popular_companies, investor
WHERE id_company_stock_amount.Symbol = popular_companies.Symbol and Investor.id = id_company_stock_amount.id;

CREATE VIEW max_for_symbol
AS
SELECT SYMBOL, MAX(sumBq) AS maxi
from people_bought_popular_companies_stock
GROUP BY symbol;

--query 3

CREATE VIEW only_one_buy
AS
SELECT Symbol, COUNT(*) as count_instances
FROM Buying
GROUP BY Symbol
Having COUNT(*)=1;

CREATE VIEW only_one_buy_dates
AS
SELECT only_one_buy.Symbol, Buying.tDate, stock.Price
FROM only_one_buy, buying, stock
WHERE only_one_buy.Symbol = Buying.Symbol and stock.tDate = Buying.tDate and Buying.Symbol=stock.Symbol;

CREATE VIEW bigger_days
AS
SELECT stock1.tDate, stock1.price, stock1.symbol
FROM stock as stock1 INNER JOIN only_one_buy_dates as stock2 ON stock1.Symbol=stock2.Symbol
WHERE stock1.tDate> stock2.tDate;

CREATE VIEW min_date
AS
SELECT bigger_days.symbol, MIN(bigger_days.tDate) next_trade_date
FROM bigger_days
GROUP BY bigger_days.symbol;

CREATE VIEW min_date_with_prices
AS
SELECT min_date.symbol, stock.tDate, stock.Price
FROM min_date INNER JOIN stock ON stock.Symbol=min_date.symbol and stock.tDate=min_date.next_trade_date;

CREATE VIEW date_symbol_groise
AS
SELECT only_one_buy_dates.tDate, only_one_buy_dates.Symbol
FROM min_date_with_prices INNER JOIN only_one_buy_dates ON min_date_with_prices.symbol = only_one_buy_dates.Symbol
WHERE min_date_with_prices.Price-only_one_buy_dates.Price > only_one_buy_dates.Price*(0.03);


--view for buy stocks

CREATE VIEW buy_stock_company
AS
SELECT id, buying.tDate, Buying.symbol, BQuantity*Price AS total_sum
FROM Buying, Stock
WHERE Stock.tDate=Buying.tDate and stock.Symbol=Buying.Symbol;
