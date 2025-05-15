import polib
from deep_translator import GoogleTranslator

def translate_po_file(input_file, output_file, target_language):
    # Load the .po file
    po = polib.pofile(input_file)
    
    # Iterate through each entry in the .po file
    for entry in po:
        if entry.msgstr.strip() == "":  # Only translate if msgstr is empty
            try:
                # Translate the msgid
                translation = GoogleTranslator(source="en", target=target_language).translate(entry.msgid)
                entry.msgstr = translation
                print(f"Translated: {entry.msgid} -> {entry.msgstr}")
            except Exception as e:
                print(f"Error translating '{entry.msgid}': {e}")
    
    # Save the translated .po file
    po.save(output_file)
    print(f"Translation completed. Saved to {output_file}")

# Example usage
input_po_file_fr = "./locale/fr/LC_MESSAGES/django.po" 
output_po_file_fr = "./locale/fr/LC_MESSAGES/django2.po" 
input_po_file_pt = "./locale/pt/LC_MESSAGES/django.po" 
output_po_file_pt = "./locale/pt/LC_MESSAGES/django2.po" 
translate_po_file(input_po_file_fr, output_po_file_fr, "fr")
translate_po_file(input_po_file_pt, output_po_file_pt, "pt")