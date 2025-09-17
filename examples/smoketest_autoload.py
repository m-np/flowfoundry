from flowfoundry.utils.functional_registry import strategies

print("Families:", strategies.list_families())
print("Chunkers:", strategies.list_names("chunking"))
print("Ingestions:", strategies.list_names("ingestion"))

fn = strategies.get("chunking", "toy_chunks")
chunks = fn("abcdefghij", size=3)
print("Chunks[0:2]:", chunks[:2])
assert chunks[0]["text"] == "abc"
assert chunks[1]["start"] == 3
print("OK ✔")
