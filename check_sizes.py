from extract_outline import extract_outline, get_font_size, clean_text
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

# Check font sizes in file02.pdf
all_sizes = []
for page_num, page_layout in enumerate(extract_pages('input/file02.pdf')):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                text = clean_text(text_line.get_text())
                if text and len(text) > 3:
                    size = get_font_size(text_line)
                    all_sizes.append(size)

print(f"Total font sizes collected: {len(all_sizes)}")
print(f"Average font size: {sum(all_sizes)/len(all_sizes):.2f}")
print(f"Min font size: {min(all_sizes):.2f}")
print(f"Max font size: {max(all_sizes):.2f}")

# Check specific sizes
from collections import Counter
size_counts = Counter([round(s, 1) for s in all_sizes])
print("\nMost common font sizes:")
for size, count in size_counts.most_common(10):
    print(f"  {size}: {count} occurrences")
