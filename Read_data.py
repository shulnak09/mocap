import owl

SERVER = "192.168.0.101"

ctx = owl.Context()
ctx.open(SERVER, "timeout=10000000")
ctx.initialize("streaming=1")

while ctx.isOpen() and ctx.property("initialized"):
    evt = ctx.nextEvent(1000000)   # 1 s timeout
    if not evt:
        continue

    if evt.type_id == owl.Type.FRAME:
        if "rigids" in evt:
            for r in evt.rigids:
                # pose = [x, y, z, qw, qx, qy, qz] or equivalent quaternion ordering
                print("RIGID", r.id, list(r.pose), r.cond)

        if "markers" in evt:
            for m in evt.markers:
                print("MARKER", m.id, (m.x, m.y, m.z), m.cond)

    elif evt.type_id == owl.Type.ERROR:
        print("ERROR", evt.name, evt.data)
        if evt.name == "fatal":
            break

ctx.done()
ctx.close()