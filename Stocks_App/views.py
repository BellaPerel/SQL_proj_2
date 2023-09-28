from django.shortcuts import render
from Stocks_App.models import Buying,Company,Stock,Investor,Transactions
from django.db import connection
from datetime import datetime
from django.contrib import messages

# Create your views here.
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request):
    return render(request, 'index.html')



def query_results(request):
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT Name,round(SUM(paid_per_date),3) as Total_Sum
                    FROM diverse_investor_amount_spent_per_date
                    GROUP BY Name
                    ORDER BY Total_Sum DESC;

                """)
        sql_res1 = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT max_for_symbol.SYMBOL as symbol,name,  sumbq as quantity
                    FROM people_bought_popular_companies_stock, max_for_symbol
                    WHERE people_bought_popular_companies_stock.sumbq = max_for_symbol.maxi and
                        people_bought_popular_companies_stock.SYMBOL = max_for_symbol.SYMBOL
                    ORDER BY SYMBOL;
                """)
        sql_res2 = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT date_symbol_groise.tDate as tdate, date_symbol_groise.Symbol as symbol, Investor.Name as name
                    FROM (date_symbol_groise INNER JOIN Buying ON date_symbol_groise.tDate=Buying.tDate  and date_symbol_groise.Symbol=Buying.Symbol)
                        INNER JOIN Investor ON Investor.ID=Buying.ID
                    ORDER BY tDate,Symbol;
                """)
        sql_res3 = dictfetchall(cursor)
    return render(request,'query_results.html', {'sql_res1':sql_res1, 'sql_res2':sql_res2, 'sql_res3':sql_res3})


def update_cash_old(transaction_sum, old_sum, id):
    with connection.cursor() as cursor:
        cursor.execute("""
                    UPDATE Investor 
                    SET availablecash = availablecash+%s-%s
                    WHERE id = %s;
                """,[int(transaction_sum),int(old_sum),id])
        #return dictfetchall(cursor)

def update_cash_new(transaction_sum, id):
    with connection.cursor() as cursor:
        cursor.execute("""
                    UPDATE Investor 
                    SET availablecash = availablecash + %s
                    WHERE id = %s;
                """,[int(transaction_sum),id])
        #return dictfetchall(cursor)


def update_Transaction(transaction_new, id, tdate):
    with connection.cursor() as cursor:
        cursor.execute("""
                    UPDATE Transactions
                    SET tquantity = %s
                    WHERE id = %s and tdate=%s;
                """,[int(transaction_new),id,tdate])
        #return dictfetchall(cursor)


def if_trans_exists(id,tdate):
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT Transactions.id,Transactions.tdate,tquantity
                    FROM Transactions
                    WHERE Transactions.id = %s and Transactions.tdate = %s;
                """,[id,tdate])
        return dictfetchall(cursor)


def insert_new_transaction(id,tdate,tquantity):
    with connection.cursor() as cursor:
        cursor.execute("""
                    INSERT INTO Transactions
                    VALUES (%s,%s,%s);
                """,[tdate,int(id),int(tquantity)])

def if_id_exists(id):
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT Investor.id
                    FROM Investor
                    WHERE Investor.id = %s;
                """,[id])
        newdict=dictfetchall(cursor)
    return newdict

def if_company_exists(symbol):
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT Company.symbol
                    FROM Company
                    WHERE Company.symbol = %s;
                """,[symbol])
        return dictfetchall(cursor)


def add_transaction(request):
    if request.method == 'POST' and request.POST:
        id = request.POST["id"]
        tdate = datetime.today().strftime("%Y-%m-%d")
        tquantity = request.POST["tquantity"]
        if len(if_id_exists(id))!=0:
            messages.error(request, "Transaction was added successfully!")
            if len(if_trans_exists(id, tdate))!=0:
                lastAmount = if_trans_exists(id, tdate)[0]['tquantity']
                update_cash_old(tquantity, lastAmount, id)
                update_Transaction(tquantity,id,tdate)
            else:
                update_cash_new(tquantity,id)
                insert_new_transaction(id,tdate,tquantity)
        else:
            messages.error(request,"this investor id doesn't exist in the DataBase! try another id.")

    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT TOP 10 tdate, id, tquantity
                    FROM Transactions
                    ORDER BY tDate DESC, id DESC ;
                """)
        sql_res4 = dictfetchall(cursor)
    return render(request, 'add_transaction.html', {'sql_res4':sql_res4})

def if_company_buyer_date_exists(id, symbol, tdate):
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT Buying.id, Buying.symbol, Buying.tdate
                    FROM Buying
                    WHERE Buying.id=%s and Buying.symbol=%s and Buying.tdate=%s;
                """,[id, symbol, tdate])
        return dictfetchall(cursor)

def if_can_buy(id):
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT availablecash
                    FROM Investor
                    WHERE Investor.id = %s
                """,[id])
        return dictfetchall(cursor)



def get_last_date_amount(symbol):
    with connection.cursor() as cursor:
        cursor.execute("""
                    SELECT TOP 1 tdate, symbol, price
                    FROM Stock
                    WHERE Stock.symbol = %s
                    ORDER BY tDate DESC;
                """,[symbol])
        return dictfetchall(cursor)

def add_stock_record(symbol,tdate,stockamount):
    with connection.cursor() as cursor:
        cursor.execute("""
                    INSERT INTO Stock
                    VALUES (%s,%s,%s);
                """, [symbol, tdate, float(stockamount)])

def insert_record_to_buying(tdate,id,symbol,bquantity):
    with connection.cursor() as cursor:
        cursor.execute("""
                    INSERT INTO Buying
                    VALUES (%s,%s,%s,%s);
                """,[tdate,int(id),symbol,int(bquantity)])


def update_available_cash(total_sum, id):
    with connection.cursor() as cursor:
        cursor.execute("""
                        UPDATE Investor
                        SET availablecash = availablecash-%s
                        WHERE Investor.id = %s
                    """,[float(total_sum), id])


def if_today_stock_exist(symbol, tdate):
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT symbol
                        FROM Stock
                        WHERE symbol=%s and tdate = %s
                    """,[symbol, tdate])
        return dictfetchall(cursor)


def buy_stocks(request):
    if request.method == 'POST' and request.POST:
        id = request.POST["id"]
        symbol = request.POST["symbol"]
        tdate = datetime.today().strftime("%Y-%m-%d")
        bquantity = request.POST["bquantity"]
        if len(if_id_exists(id))!=0 and len(if_company_exists(symbol))!=0:
            if len(if_company_buyer_date_exists(id, symbol, tdate))==0:
                stockamount = get_last_date_amount(symbol)[0]['price']
                if float(if_can_buy(id)[0]['availablecash']) >= float(stockamount)*float(bquantity):
                    if len(if_today_stock_exist(symbol, tdate))==0:
                        add_stock_record(symbol, tdate, stockamount)
                    update_available_cash(float(stockamount)*float(bquantity), id)
                    insert_record_to_buying(tdate,id,symbol,bquantity)
                    messages.error(request,
                                   "the buying was added successfully!")
                else:
                    messages.error(request,
                                   "this investor doesn't have enough money for this buying! try something else.")
            else:
                messages.error(request,
                               "this investor id already bought stocks of this company today! try another input")
        else:
            if len(if_id_exists(id))==0 and len(if_company_exists(symbol))==0:
                messages.error(request,"this investor id and this company doesn't exist in the DataBase! try another id and company.")
            else:
                if len(if_company_exists(symbol))==0:
                    messages.error(request, "this company doesn't exist in the DataBase! try another company.")
                else:
                    messages.error(request, "this investor id doesn't exist in the DataBase! try another id.")

    with connection.cursor() as cursor:
        cursor.execute("""
             SELECT TOP 10 tdate,id, symbol, round(total_sum,2) as totalsum
            FROM buy_stock_company
            ORDER BY round(total_sum,2) DESC, id DESC ;       
                """)
        sql_res5 = dictfetchall(cursor)
    return render(request, 'buy_stocks.html',{'sql_res5':sql_res5})