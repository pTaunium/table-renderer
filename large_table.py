from table_renderer import Table

table = Table()
# table.set_width(4000)
table.set_border(width=1, color="black", style="solid")

for x in range(50):
    for y in range(50):
        table.cell(x, y).set_text(f"{x * y}")

table.to_image("large_table.webp")
