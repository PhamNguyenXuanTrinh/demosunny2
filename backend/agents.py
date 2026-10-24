import json,uuid
from .db import connect,transaction
from .security import now
AGENTS=('Kho','Sản xuất','Kế toán','Tài chính','Marketing','Kinh doanh','Nhân sự','Chất lượng','Tài sản','Kiểm toán')

def evaluate(trigger='manual',actor='system'):
 with connect() as c:
  low=[dict(x) for x in c.execute('''SELECT i.sku,i.name,i.standard_qty,COALESCE(SUM(m.quantity_delta),0) stock FROM inventory_items i LEFT JOIN stock_movements m ON m.item_id=i.id GROUP BY i.id HAVING i.standard_qty>0 AND stock<=i.standard_qty*.4''')]
  orders=c.execute('SELECT COUNT(*) FROM sales_orders').fetchone()[0]
  purchases=c.execute('SELECT COUNT(*) FROM purchases').fetchone()[0]
  assets=c.execute('SELECT COUNT(*) FROM assets').fetchone()[0]
  costs=c.execute('SELECT COALESCE(SUM(amount),0) FROM cost_transactions').fetchone()[0]
 results={
 'Kho':{'alerts':low,'count':len(low)},'Sản xuất':{'note':'Chưa có đủ dữ liệu hiệu suất theo ca để kết luận'},
 'Kế toán':{'purchase_count':purchases,'note':'Chưa đối soát ngân hàng'},
 'Tài chính':{'recorded_cost':costs,'target_3pct':round(costs*.03),'note':'Chưa xác minh tiết kiệm thực tế'},
 'Marketing':{'note':'Cần gắn nguồn chiến dịch với đơn hàng'},'Kinh doanh':{'order_count':orders},
 'Nhân sự':{'note':'Chưa có đủ dữ liệu chấm công để kết luận'},'Chất lượng':{'note':'Cần kết quả QC theo lô'},
 'Tài sản':{'asset_count':assets},'Kiểm toán':{'note':'Các kết luận chưa có bằng chứng được đánh dấu chưa xác minh'}}
 run_id=str(uuid.uuid4())
 with transaction() as c:
  for name in AGENTS:
   c.execute('INSERT INTO agent_evaluations VALUES(?,?,?,?,?,?)',(str(uuid.uuid4()),name,trigger,json.dumps(results[name],ensure_ascii=False),now(),'sqlite_rules'))
 return {'run_id':run_id,'trigger':trigger,'mode':'sqlite_rules_not_llm','results':results,'commander':{'priority':'Kho' if low else 'Cần bổ sung dữ liệu','requires_human_approval':True,'conflicts_checked':False}}
