

def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        'INSERT INTO batches (reference, sku, _purchased_quantity, eta)'
        'VALUES (:ref, :sku, :qty, :eta)',
        dict(ref=ref, sku=sku, qty=qty, eta=eta)
    )

def get_allocated_batch_ref(session, orderid, sku):
    [[orderlineid]] = session.execute(
        'SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku',
        dict(orderid=orderid, sku=sku)
    )

    [[batchref]] = session.execute(
        'SELECT b.reference FROM allocations JOIN batches AS b'
        'ON batch_id=b.id WHERE orderline_id=:orderlineid',
        dict(orderlineid=orderlineid)
    )

    return batchref