use test
set names utf8;

-- 1. Выбрать все товары (все поля)
select * from product

-- 2. Выбрать названия всех автоматизированных складов
SELECT NAME FROM store
WHERE is_automated = 1


-- 3. Посчитать общую сумму в деньгах всех продаж
SELECT SUM(total) FROM sale

-- 4. Получить уникальные store_id всех складов, с которых была хоть одна продажа
SELECT DISTINCT(store_id) FROM store
JOIN sale USING(store_id)


-- 5. Получить уникальные store_id всех складов, с которых не было ни одной продажи
SELECT DISTINCT(store_id) FROM store
LEFT JOIN sale USING(store_id) 
WHERE quantity IS NULL

-- 6. Получить для каждого товара название и среднюю стоимость единицы товара avg(total/quantity), если товар не продавался, он не попадает в отчет.
SELECT product.name, AVG(sale.total/sale.quantity) FROM product 
JOIN sale USING(product_id)
GROUP BY product.name

-- 7. Получить названия всех продуктов, которые продавались только с единственного склада
select name from product 
natural join sale 
group by product_id 
having count(distinct store_id) = 1

-- 8. Получить названия всех складов, с которых продавался только один продукт
select name from store 
natural join sale 
group by store_id 
having count(distinct product_id) = 1

-- 9. Выберите все ряды (все поля) из продаж, в которых сумма продажи (total) максимальна (равна максимальной из всех встречающихся)
select * from sale 
where total = (select max(total) from sale);

-- 10. Выведите дату самых максимальных продаж, если таких дат несколько, то самую раннюю из них
select date from sale 
group by date 
order by sum(total) DESC, date ASC LIMIT 1
