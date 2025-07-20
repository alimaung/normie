#!/usr/bin/env python3
"""
PDF Form Field Testing GUI

A graphical interface for testing PDF form field mappings with:
- PDF display with zoom/pan
- Field selection and testing
- Real-time form updates
- Side-by-side original/modified view
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import fitz  # PyMuPDF
import json
import os
import shutil
import io
from datetime import datetime
from PIL import Image, ImageTk
import threading
import tempfile

class PDFFormGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Form Field Tester")
        self.root.geometry("1400x900")
        
        # Data
        self.pdf_path = None
        self.json_path = None
        self.field_mapping = {}
        self.current_doc = None
        self.temp_pdf_path = None
        self.zoom_level = 1.0
        self.current_page = 0
        self.total_pages = 0
        
        # Step-by-step testing
        self.step_mode = False
        self.step_tests = []  # List of (field_id, value, description) tuples
        self.current_step = 0
        self.step_results = {}  # Store validation results {step_index: {'result': 'correct'|'wrong'|'skip', 'correct_value': value}}
        
        # GUI setup
        self.setup_gui()
        
        # Try to load default files
        self.load_default_files()
    
    def setup_gui(self):
        """Setup the GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar
        self.setup_toolbar(main_frame)
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Left panel - PDF display
        self.setup_pdf_panel(content_frame)
        
        # Right panel - Field controls (with scrolling)
        self.setup_field_panel(content_frame)
        
        # Bottom status bar
        self.setup_status_bar(main_frame)
    
    def setup_toolbar(self, parent):
        """Setup the top toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # File operations
        ttk.Button(toolbar, text="Load PDF", command=self.load_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Load JSON", command=self.load_json).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # PDF navigation
        ttk.Button(toolbar, text="◀", command=self.prev_page).pack(side=tk.LEFT, padx=(0, 2))
        self.page_label = ttk.Label(toolbar, text="Page 0/0")
        self.page_label.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="▶", command=self.next_page).pack(side=tk.LEFT, padx=(0, 5))
        
        # Zoom controls
        ttk.Button(toolbar, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="Fit", command=self.zoom_fit).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Form operations
        ttk.Button(toolbar, text="Fill All Fields", command=self.fill_all_fields).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Reset Form", command=self.reset_form).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save PDF", command=self.save_pdf).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Step-by-step testing
        ttk.Button(toolbar, text="Start Step Test", command=self.start_step_test).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="◀ Prev Step", command=self.prev_step).pack(side=tk.LEFT, padx=(0, 2))
        self.step_label = ttk.Label(toolbar, text="Step Mode: Off")
        self.step_label.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="Next Step ▶", command=self.next_step).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Stop Step Test", command=self.stop_step_test).pack(side=tk.LEFT, padx=(0, 5))
    
    def setup_pdf_panel(self, parent):
        """Setup the PDF display panel"""
        pdf_frame = ttk.LabelFrame(parent, text="PDF Display")
        pdf_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # PDF canvas with scrollbars
        canvas_frame = ttk.Frame(pdf_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.pdf_canvas = tk.Canvas(canvas_frame, bg='white')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.pdf_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.pdf_canvas.xview)
        
        self.pdf_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.pdf_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Mouse bindings for pan
        self.pdf_canvas.bind("<Button-1>", self.start_pan)
        self.pdf_canvas.bind("<B1-Motion>", self.pan_canvas)
        self.pdf_canvas.bind("<MouseWheel>", self.mouse_wheel)
    
    def setup_field_panel(self, parent):
        """Setup the field control panel with scrolling"""
        # Create outer frame for scrolling
        field_outer_frame = ttk.Frame(parent)
        field_outer_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        field_outer_frame.configure(width=400)
        
        # Create canvas and scrollbar for scrolling
        field_canvas = tk.Canvas(field_outer_frame, width=380)
        field_scrollbar = ttk.Scrollbar(field_outer_frame, orient="vertical", command=field_canvas.yview)
        field_canvas.configure(yscrollcommand=field_scrollbar.set)
        
        # Create scrollable frame
        field_frame = ttk.LabelFrame(field_canvas, text="Field Controls")
        field_frame.bind('<Configure>', lambda e: field_canvas.configure(scrollregion=field_canvas.bbox("all")))
        
        # Pack scrollbar and canvas
        field_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        field_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        field_canvas.create_window((0, 0), window=field_frame, anchor="nw")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            field_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        field_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Field list
        list_frame = ttk.Frame(field_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(list_frame, text="Form Fields:").pack(anchor=tk.W)
        
        # Treeview for fields
        columns = ('ID', 'Name', 'Type', 'Value')
        self.field_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.field_tree.heading(col, text=col)
            self.field_tree.column(col, width=80)
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.field_tree.yview)
        self.field_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.field_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.field_tree.bind('<<TreeviewSelect>>', self.on_field_select)
        
        # Field editor
        editor_frame = ttk.LabelFrame(field_frame, text="Field Editor")
        editor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Field info
        self.field_info_label = ttk.Label(editor_frame, text="Select a field to edit")
        self.field_info_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Value editor
        self.value_frame = ttk.Frame(editor_frame)
        self.value_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Test buttons
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Test Field", command=self.test_selected_field).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Field", command=self.clear_selected_field).pack(side=tk.LEFT)
        
        # Step testing validation panel (permanent section)
        self.setup_step_validation_panel(field_frame)
        
        # Log area
        log_frame = ttk.LabelFrame(field_frame, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, width=50)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_step_validation_panel(self, parent):
        """Setup the step validation panel as a permanent section"""
        # Create the validation frame - always visible but initially disabled
        self.step_validation_frame = ttk.LabelFrame(parent, text="Step Test Validation")
        self.step_validation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Current step info
        self.current_step_label = ttk.Label(self.step_validation_frame, text="Click 'Start Step Test' to begin", 
                                          font=('TkDefaultFont', 10, 'bold'), foreground='gray')
        self.current_step_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Test result question
        self.test_question_label = ttk.Label(self.step_validation_frame, text="Step testing not active", 
                                           foreground='gray')
        self.test_question_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Validation buttons
        validation_buttons = ttk.Frame(self.step_validation_frame)
        validation_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        self.correct_btn = ttk.Button(validation_buttons, text="✓ Correct", command=self.mark_step_correct, state='disabled')
        self.correct_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.wrong_btn = ttk.Button(validation_buttons, text="✗ No Change", command=self.mark_step_no_change, state='disabled')
        self.wrong_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.different_btn = ttk.Button(validation_buttons, text="⚠ Different Field", command=self.mark_step_different_field, state='disabled')
        self.different_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.skip_btn = ttk.Button(validation_buttons, text="? Skip", command=self.mark_step_skip, state='disabled')
        self.skip_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Different field input (for field targeting issues)
        self.different_field_frame = ttk.Frame(self.step_validation_frame)
        
        # Label for different field input
        self.different_field_label = ttk.Label(self.different_field_frame, text="Which field does this actually target?")
        self.different_field_label.pack(anchor=tk.W)
        
        # Field ID input
        self.different_field_var = tk.StringVar()
        self.different_field_entry = ttk.Entry(self.different_field_frame, textvariable=self.different_field_var)
        self.different_field_entry.pack(fill=tk.X, pady=2)
        
        # Help text
        ttk.Label(self.different_field_frame, text="Enter the field ID that actually changes (or 'none' if no field changes)", 
                 font=('TkDefaultFont', 8)).pack(anchor=tk.W)
        
        # Apply button
        ttk.Button(self.different_field_frame, text="Save & Continue", 
                  command=self.apply_different_field).pack(pady=2)
    
    def setup_status_bar(self, parent):
        """Setup the status bar"""
        self.status_bar = ttk.Label(parent, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def load_default_files(self):
        """Try to load default files"""
        if os.path.exists("pdf.pdf"):
            self.pdf_path = "pdf.pdf"
            self.load_pdf_file()
        
        if os.path.exists("pdf_dict.json"):
            self.json_path = "pdf_dict.json"
            self.load_json_file()
    
    def load_pdf(self):
        """Load PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.pdf_path = file_path
            self.load_pdf_file()
    
    def load_json(self):
        """Load JSON mapping file"""
        file_path = filedialog.askopenfilename(
            title="Select JSON mapping file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.json_path = file_path
            self.load_json_file()
    
    def load_pdf_file(self):
        """Load the PDF file"""
        try:
            if self.current_doc:
                self.current_doc.close()
            
            # Create temporary copy
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.temp_pdf_path = f"temp_gui_{timestamp}.pdf"
            shutil.copy2(self.pdf_path, self.temp_pdf_path)
            
            self.current_doc = fitz.open(self.temp_pdf_path)
            self.total_pages = len(self.current_doc)
            self.current_page = 0
            
            self.log(f"Loaded PDF: {os.path.basename(self.pdf_path)} ({self.total_pages} pages)")
            self.update_status(f"PDF loaded: {os.path.basename(self.pdf_path)}")
            
            self.display_pdf_page()
            self.populate_field_list()
            
        except Exception as e:
            self.log(f"Error loading PDF: {e}")
            messagebox.showerror("Error", f"Could not load PDF: {e}")
    
    def load_json_file(self):
        """Load the JSON mapping file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.field_mapping = json.load(f)
            
            self.log(f"Loaded JSON mapping: {os.path.basename(self.json_path)} ({len(self.field_mapping)} fields)")
            self.update_status(f"JSON loaded: {os.path.basename(self.json_path)}")
            
            self.populate_field_list()
            
        except Exception as e:
            self.log(f"Error loading JSON: {e}")
            messagebox.showerror("Error", f"Could not load JSON: {e}")
    
    def populate_field_list(self):
        """Populate the field list"""
        # Clear existing items
        for item in self.field_tree.get_children():
            self.field_tree.delete(item)
        
        if not self.field_mapping:
            return
        
        # Add fields to tree
        for field_id, field_info in self.field_mapping.items():
            field_name = field_info.get('name', 'Unknown')
            field_type = field_info.get('type', 'Unknown')
            
            # Get current value from PDF if available
            current_value = self.get_field_value(field_id)
            
            self.field_tree.insert('', 'end', values=(field_id, field_name, field_type, current_value))
    
    def get_field_value(self, field_id):
        """Get current value of a field from PDF"""
        if not self.current_doc:
            return ""
        
        try:
            possible_names = [
                field_id,
                f"field_{field_id}",
                f"Field{field_id}",
                self.field_mapping.get(field_id, {}).get("name", "")
            ]
            
            for page in self.current_doc:
                for widget in page.widgets():
                    if widget.field_name in possible_names:
                        return str(widget.field_value or "")
            
            return ""
        except Exception as e:
            self.log(f"Error getting field value for {field_id}: {e}")
            return ""
    
    def display_pdf_page(self):
        """Display the current PDF page"""
        if not self.current_doc:
            return
        
        try:
            page = self.current_doc[self.current_page]
            
            # Render page to image
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))
            self.pdf_image = ImageTk.PhotoImage(img)
            
            # Update canvas
            self.pdf_canvas.delete("all")
            self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=self.pdf_image)
            
            # Update scroll region
            self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all"))
            
            # Update page label
            self.page_label.config(text=f"Page {self.current_page + 1}/{self.total_pages}")
            
        except Exception as e:
            self.log(f"Error displaying PDF page: {e}")
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_pdf_page()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_pdf_page()
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level *= 1.2
        self.display_pdf_page()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level /= 1.2
        self.display_pdf_page()
    
    def zoom_fit(self):
        """Fit to window"""
        self.zoom_level = 1.0
        self.display_pdf_page()
    
    def start_pan(self, event):
        """Start panning"""
        self.pdf_canvas.scan_mark(event.x, event.y)
    
    def pan_canvas(self, event):
        """Pan the canvas"""
        self.pdf_canvas.scan_dragto(event.x, event.y, gain=1)
    
    def mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_field_select(self, event):
        """Handle field selection"""
        selection = self.field_tree.selection()
        if not selection:
            return
        
        item = self.field_tree.item(selection[0])
        field_id = item['values'][0]
        
        self.setup_field_editor(field_id)
    
    def setup_field_editor(self, field_id):
        """Setup the field editor for selected field"""
        if field_id not in self.field_mapping:
            return
        
        field_info = self.field_mapping[field_id]
        field_name = field_info.get('name', 'Unknown')
        field_type = field_info.get('type', 'Unknown')
        
        # Update info label
        self.field_info_label.config(text=f"Field {field_id}: {field_name} ({field_type})")
        
        # Clear existing editor
        for widget in self.value_frame.winfo_children():
            widget.destroy()
        
        # Create appropriate editor
        if field_type == 'text':
            self.setup_text_editor(field_id)
        elif field_type == 'btn':
            self.setup_button_editor(field_id)
        elif field_type == 'sig':
            ttk.Label(self.value_frame, text="Signature field - cannot edit").pack()
    
    def setup_text_editor(self, field_id):
        """Setup text field editor"""
        current_value = self.get_field_value(field_id)
        
        ttk.Label(self.value_frame, text="Value:").pack(anchor=tk.W)
        self.text_var = tk.StringVar(value=current_value)
        entry = ttk.Entry(self.value_frame, textvariable=self.text_var, width=40)
        entry.pack(fill=tk.X, pady=2)
        
        # Store field_id for later use
        self.current_field_id = field_id
    
    def setup_button_editor(self, field_id):
        """Setup button field editor"""
        field_info = self.field_mapping[field_id]
        values = field_info.get('values', {})
        
        current_value = self.get_field_value(field_id)
        
        ttk.Label(self.value_frame, text="Options:").pack(anchor=tk.W)
        
        self.button_var = tk.StringVar()
        
        # Find current selection
        for display_val, pdf_val in values.items():
            if pdf_val == current_value:
                self.button_var.set(display_val)
                break
        
        # Create radio buttons
        for display_val in values.keys():
            ttk.Radiobutton(
                self.value_frame, 
                text=display_val, 
                variable=self.button_var, 
                value=display_val
            ).pack(anchor=tk.W)
        
        # Store field_id for later use
        self.current_field_id = field_id
    
    def test_selected_field(self):
        """Test the selected field"""
        if not hasattr(self, 'current_field_id'):
            return
        
        field_id = self.current_field_id
        field_info = self.field_mapping[field_id]
        field_type = field_info.get('type', 'Unknown')
        
        try:
            if field_type == 'text':
                value = self.text_var.get()
                self.set_text_field(field_id, value)
            elif field_type == 'btn':
                display_value = self.button_var.get()
                values = field_info.get('values', {})
                if display_value in values:
                    pdf_value = values[display_value]
                    self.set_button_field(field_id, pdf_value)
            
            # Refresh display
            self.display_pdf_page()
            self.populate_field_list()
            
            self.log(f"Updated field {field_id}")
            
        except Exception as e:
            self.log(f"Error updating field {field_id}: {e}")
    
    def clear_selected_field(self):
        """Clear the selected field"""
        if not hasattr(self, 'current_field_id'):
            return
        
        field_id = self.current_field_id
        
        try:
            self.set_text_field(field_id, "")
            
            # Refresh display
            self.display_pdf_page()
            self.populate_field_list()
            
            self.log(f"Cleared field {field_id}")
            
        except Exception as e:
            self.log(f"Error clearing field {field_id}: {e}")
    
    def set_text_field(self, field_id, value):
        """Set text field value"""
        if not self.current_doc:
            return False
        
        possible_names = [
            field_id,
            f"field_{field_id}",
            f"Field{field_id}",
            self.field_mapping.get(field_id, {}).get("name", "")
        ]
        
        for page in self.current_doc:
            for widget in page.widgets():
                if widget.field_name in possible_names:
                    widget.field_value = str(value)
                    widget.update()
                    return True
        
        return False
    
    def set_button_field(self, field_id, pdf_value):
        """Set button field value"""
        if not self.current_doc:
            return False
        
        possible_names = [
            field_id,
            f"field_{field_id}",
            f"Field{field_id}",
            self.field_mapping.get(field_id, {}).get("name", "")
        ]
        
        success = False
        for page in self.current_doc:
            for widget in page.widgets():
                if widget.field_name in possible_names:
                    try:
                        # Convert PDF value to PyMuPDF format
                        clean_value = pdf_value
                        
                        # Strip leading "/" if present
                        if isinstance(pdf_value, str) and pdf_value.startswith("/"):
                            clean_value = pdf_value[1:]
                        
                        # For radio buttons (numeric values), convert to int and add 1 (radio buttons start at 1, not 0)
                        if isinstance(clean_value, str) and clean_value.isdigit():
                            clean_value = int(clean_value) + 1
                        
                        # Try setting the value
                        widget.field_value = clean_value
                        widget.update()
                        success = True
                        self.log(f"    Set button field '{widget.field_name}' to '{clean_value}' (from '{pdf_value}')")
                        break
                    except Exception as e:
                        self.log(f"    Error setting button field {widget.field_name}: {e}")
                        # Try alternative: set original value
                        try:
                            widget.field_value = pdf_value
                            widget.update()
                            success = True
                            self.log(f"    Set button field '{widget.field_name}' to '{pdf_value}' (fallback)")
                            break
                        except Exception as e2:
                            self.log(f"    Fallback also failed: {e2}")
        
        if not success:
            self.log(f"    Warning: Could not find button field for {field_id}")
        
        return success
    
    def fill_all_fields(self):
        """Fill all fields with mock data"""
        if not self.current_doc or not self.field_mapping:
            return
        
        # Mock data
        text_data = {
            "1": "2025-TEST-001",
            "2a": "Max Mustermann",
            "2b": "01.01.2025",
            "3": "Test Chemikalie",
            "4": "EXT-12345",
            "7": "REACH-001",
            "8": "Test Lieferant GmbH",
            "10": "Test Verwendungszweck",
            "16": "kg",
            "17a": "10"
        }
        
        button_data = {
            "5": "Neubedarf",
            "6": "Stoff",
            "13": "Ja (Produktzulassung ist erforderlich)",
            "14": "kurzfristig",
            "15a": "Ja",
            "18a": "Ja"
        }
        
        updated_count = 0
        
        # Update text fields
        for field_id, value in text_data.items():
            if field_id in self.field_mapping:
                if self.set_text_field(field_id, value):
                    updated_count += 1
        
        # Update button fields
        for field_id, display_value in button_data.items():
            if field_id in self.field_mapping:
                field_info = self.field_mapping[field_id]
                if field_info.get("type") == "btn":
                    values = field_info.get("values", {})
                    if display_value in values:
                        pdf_value = values[display_value]
                        if self.set_button_field(field_id, pdf_value):
                            updated_count += 1
        
        # Refresh display
        self.display_pdf_page()
        self.populate_field_list()
        
        self.log(f"Filled {updated_count} fields with mock data")
    
    def reset_form(self):
        """Reset form to original state"""
        if not self.pdf_path:
            return
        
        try:
            # Close current document
            if self.current_doc:
                self.current_doc.close()
            
            # Create new temporary copy
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
                os.remove(self.temp_pdf_path)
            
            self.temp_pdf_path = f"temp_gui_{timestamp}.pdf"
            shutil.copy2(self.pdf_path, self.temp_pdf_path)
            
            # Reopen
            self.current_doc = fitz.open(self.temp_pdf_path)
            
            # Refresh display
            self.display_pdf_page()
            self.populate_field_list()
            
            self.log("Form reset to original state")
            
        except Exception as e:
            self.log(f"Error resetting form: {e}")
    
    def save_pdf(self):
        """Save the current PDF"""
        if not self.current_doc:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_doc.saveIncr()
                shutil.copy2(self.temp_pdf_path, file_path)
                self.log(f"PDF saved to: {file_path}")
                messagebox.showinfo("Success", f"PDF saved to:\n{file_path}")
            except Exception as e:
                self.log(f"Error saving PDF: {e}")
                messagebox.showerror("Error", f"Could not save PDF: {e}")
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
    
    def start_step_test(self):
        """Start step-by-step field testing"""
        if not self.field_mapping:
            messagebox.showwarning("Warning", "Please load a JSON mapping file first.")
            return
        
        self.step_mode = True
        self.current_step = 0
        self.step_tests = []
        
        # Generate all test combinations
        self.generate_step_tests()
        
        if not self.step_tests:
            messagebox.showinfo("Info", "No testable fields found.")
            return
        
        self.log(f"Starting step-by-step testing with {len(self.step_tests)} steps")
        self.step_results = {}  # Reset results
        self.update_step_display()
        self.show_step_validation_panel()
        self.execute_current_step()
    
    def generate_step_tests(self):
        """Generate all field/value combinations for testing"""
        # Mock data for text fields
        text_mock_data = {
            "1": "2025-TEST-001",
            "2a": "Max Mustermann",
            "2b": "01.01.2025",
            "2c": "Entwicklung",
            "2d": "+49 123 456789",
            "3": "Test Chemikalie ABC",
            "4": "EXT-12345",
            "7": "REACH-001",
            "8": "Test Lieferant GmbH",
            "9": "Test Hersteller AG",
            "10": "Verwendung für Prototypentwicklung und Testverfahren",
            "11": "Engine Program X",
            "12a": "Standort München",
            "12b": "Team Engineering",
            "16": "kg",
            "17a": "10",
            "17b": "wöchentlich",
            "17c": "2 kg",
            "18e": "DIN EN 12345",
            "19": "Zusätzliche Erläuterungen zum Test",
            "20": "Verweis auf Antrag 2024-ABC-001",
            "21": "15.02.2025",
            "25a": "Dr. Umwelt",
            "25c": "10.01.2025",
            "31": "Umweltschutz Erläuterungen",
            "32a": "Dr. Sicherheit",
            "32c": "11.01.2025",
            "38": "Arbeitsschutz Erläuterungen",
            "51": "TKZ-98765",
            "52": "Abschließende Erläuterungen"
        }
        
        # Sort field IDs for consistent order
        sorted_fields = sorted(self.field_mapping.keys(), key=lambda x: self.natural_sort_key(x))
        
        for field_id in sorted_fields:
            field_info = self.field_mapping[field_id]
            field_type = field_info.get('type', 'unknown')
            field_name = field_info.get('name', 'Unknown')
            
            if field_type == 'text':
                # Single test for text fields
                test_value = text_mock_data.get(field_id, f"Test value for {field_id}")
                description = f"Text Field {field_id}: {field_name}"
                self.step_tests.append((field_id, test_value, description, 'text'))
                
            elif field_type == 'btn':
                # Multiple tests for button fields (one for each value)
                values = field_info.get('values', {})
                for display_value, pdf_value in values.items():
                    description = f"Button Field {field_id}: {field_name} = '{display_value}'"
                    self.step_tests.append((field_id, pdf_value, description, 'btn', display_value))
                    
            elif field_type == 'sig':
                # Skip signature fields but log them
                description = f"Signature Field {field_id}: {field_name} (SKIPPED)"
                self.step_tests.append((field_id, None, description, 'sig'))
    
    def natural_sort_key(self, text):
        """Natural sorting key for field IDs (handles 1, 2a, 2b, 10, etc.)"""
        import re
        parts = re.split(r'(\d+)', text)
        return [int(part) if part.isdigit() else part for part in parts]
    
    def execute_current_step(self):
        """Execute the current step"""
        if not self.step_mode or self.current_step >= len(self.step_tests):
            return
        
        # Reset form to empty state first
        self.reset_form()
        
        # Get current test
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        value = step_data[1]
        description = step_data[2]
        field_type = step_data[3]
        
        self.log(f"Step {self.current_step + 1}: {description}")
        
        # Skip signature fields
        if field_type == 'sig':
            self.log("  → Skipped (signature field)")
            return
        
        # Apply the field value
        try:
            if field_type == 'text':
                success = self.set_text_field(field_id, value)
                if success:
                    self.log(f"  → Set text field to: '{value}'")
                else:
                    self.log(f"  → Failed to set text field")
                    
            elif field_type == 'btn':
                display_value = step_data[4] if len(step_data) > 4 else "Unknown"
                success = self.set_button_field(field_id, value)
                if success:
                    self.log(f"  → Set button field to: '{display_value}' (PDF value: '{value}')")
                else:
                    self.log(f"  → Failed to set button field")
            
            # Refresh display
            self.display_pdf_page()
            self.populate_field_list()
            
            # Highlight the current field in the list
            self.highlight_field_in_list(field_id)
            
            # Update validation panel
            self.update_validation_panel()
            
        except Exception as e:
            self.log(f"  → Error: {e}")
    
    def highlight_field_in_list(self, field_id):
        """Highlight the current field in the field list"""
        # Clear previous selections
        for item in self.field_tree.selection():
            self.field_tree.selection_remove(item)
        
        # Find and select the current field
        for item in self.field_tree.get_children():
            values = self.field_tree.item(item)['values']
            if values[0] == field_id:  # Field ID is in first column
                self.field_tree.selection_set(item)
                self.field_tree.see(item)
                self.field_tree.focus(item)
                break
    
    def next_step(self):
        """Go to next step"""
        if not self.step_mode:
            return
        
        if self.current_step < len(self.step_tests) - 1:
            self.current_step += 1
            self.update_step_display()
            self.execute_current_step()
        else:
            self.log("Reached end of step testing")
            messagebox.showinfo("Complete", "Step-by-step testing completed!")
    
    def prev_step(self):
        """Go to previous step"""
        if not self.step_mode:
            return
        
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_display()
            self.execute_current_step()
        else:
            self.log("At beginning of step testing")
    
    def update_step_display(self):
        """Update the step display label"""
        if self.step_mode and self.step_tests:
            current_test = self.step_tests[self.current_step]
            step_info = f"Step {self.current_step + 1}/{len(self.step_tests)}: {current_test[0]}"
            self.step_label.config(text=step_info)
        else:
            self.step_label.config(text="Step Mode: Off")
    
    def stop_step_test(self):
        """Stop step-by-step testing"""
        self.step_mode = False
        self.step_tests = []
        self.current_step = 0
        self.update_step_display()
        self.hide_step_validation_panel()
        self.log("Step-by-step testing stopped")
        
        # Show results summary
        self.show_test_results_summary()
        
        # Reset form
        self.reset_form()
    
    def show_step_validation_panel(self):
        """Enable the step validation panel"""
        # Enable the validation buttons
        self.correct_btn.config(state='normal')
        self.wrong_btn.config(state='normal')
        self.different_btn.config(state='normal')
        self.skip_btn.config(state='normal')
        
        # Update text color to active
        self.current_step_label.config(foreground='black')
        self.test_question_label.config(foreground='black')
        
        # Make sure different field frame is hidden initially
        self.different_field_frame.pack_forget()
        
        self.log("✓ Step validation panel enabled")
    
    def hide_step_validation_panel(self):
        """Disable the step validation panel"""
        # Disable the validation buttons
        self.correct_btn.config(state='disabled')
        self.wrong_btn.config(state='disabled')
        self.different_btn.config(state='disabled')
        self.skip_btn.config(state='disabled')
        
        # Update text color to inactive
        self.current_step_label.config(text="Click 'Start Step Test' to begin", foreground='gray')
        self.test_question_label.config(text="Step testing not active", foreground='gray')
        
        # Hide different field frame
        self.different_field_frame.pack_forget()
        
        self.log("✓ Step validation panel disabled")
    
    def update_validation_panel(self):
        """Update the validation panel with current step info"""
        if not self.step_mode or self.current_step >= len(self.step_tests):
            return
        
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        description = step_data[2]
        field_type = step_data[3]
        
        # Update step label
        self.current_step_label.config(text=f"Step {self.current_step + 1}/{len(self.step_tests)}: {description}")
        
        # Update question based on field type
        if field_type == 'text':
            self.test_question_label.config(text=f"Is the text field '{field_id}' filled correctly?")
        elif field_type == 'btn':
            display_value = step_data[4] if len(step_data) > 4 else "Unknown"
            self.test_question_label.config(text=f"Is '{display_value}' selected correctly in field '{field_id}'?")
        elif field_type == 'sig':
            self.test_question_label.config(text="Signature field - automatically skipped")
        
        # Hide different field input initially
        self.different_field_frame.pack_forget()
    
    def mark_step_correct(self):
        """Mark current step as correct"""
        if not self.step_mode:
            return
        
        self.step_results[self.current_step] = {'result': 'correct'}
        self.log(f"  ✓ Marked as CORRECT")
        
        # Auto-advance to next step
        self.next_step()
    
    def mark_step_no_change(self):
        """Mark current step as no change (field mapping doesn't work)"""
        if not self.step_mode:
            return
        
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        
        self.step_results[self.current_step] = {
            'result': 'no_change',
            'field_id': field_id,
            'issue': 'Field mapping does not work - no visible change in PDF'
        }
        
        self.log(f"  ✗ Marked as NO CHANGE - field mapping doesn't work")
        self.next_step()
    
    def mark_step_different_field(self):
        """Mark current step as targeting different field"""
        if not self.step_mode:
            return
        
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        
        # Show input to specify which field it actually targets
        self.show_different_field_input()
        
        self.log(f"  ⚠ Field {field_id} targets different field - specify which one")
    
    def show_different_field_input(self):
        """Show input for specifying which field actually changes"""
        if not self.step_mode:
            return
        
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        
        # Update label
        self.different_field_label.config(text=f"Field {field_id} targets which field instead?")
        
        # Clear previous input
        self.different_field_var.set("")
        
        # Show the different field frame
        self.different_field_frame.pack(fill=tk.X, padx=5, pady=5, in_=self.step_validation_frame)
        
        # Focus on text entry
        self.different_field_entry.focus_set()
    
    def apply_different_field(self):
        """Apply the different field mapping"""
        if not self.step_mode:
            return
        
        different_field = self.different_field_var.get().strip()
        if not different_field:
            messagebox.showwarning("Warning", "Please enter a field ID or 'none'.")
            return
        
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        
        # Store the different field mapping
        self.step_results[self.current_step] = {
            'result': 'different_field',
            'intended_field': field_id,
            'actual_field': different_field if different_field.lower() != 'none' else None,
            'issue': f'Field {field_id} actually targets field {different_field}'
        }
        
        self.log(f"  ⚠ Field {field_id} actually targets: {different_field}")
        
        # Hide different field input
        self.different_field_frame.pack_forget()
        
        # Auto-advance to next step
        self.next_step()
    
    def mark_step_skip(self):
        """Mark current step as skipped"""
        if not self.step_mode:
            return
        
        self.step_results[self.current_step] = {'result': 'skip'}
        self.log(f"  ? Marked as SKIPPED")
        
        # Auto-advance to next step
        self.next_step()
    
    def show_alternative_values_button(self):
        """Show alternative value selection for button fields"""
        if not self.step_mode:
            return
        
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        
        if field_id in self.field_mapping:
            field_info = self.field_mapping[field_id]
            if field_info.get('type') == 'btn':
                values = field_info.get('values', {})
                
                # Update label
                self.alt_value_label.config(text=f"Select correct value for field {field_id}:")
                
                # Populate combobox with available values
                self.alt_value_combo['values'] = list(values.keys())
                self.alt_value_combo.set('')  # Clear selection
                
                # Show combo, hide text entry
                self.alt_value_combo.pack(fill=tk.X, pady=2)
                self.alt_text_entry.pack_forget()
                
                # Show the alternative value frame
                self.alt_value_frame.pack(fill=tk.X, padx=5, pady=5, in_=self.step_validation_frame)
                
                self.log(f"  → Select the correct value for button field {field_id}")
                self.log(f"    Available options: {', '.join(values.keys())}")
    
    def show_alternative_values_text(self):
        """Show alternative value selection for text fields"""
        if not self.step_mode:
            return
        
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        current_value = step_data[1]
        
        # Update label
        self.alt_value_label.config(text=f"Enter correct value for field {field_id}:")
        
        # Set current value in text entry
        self.alt_text_var.set(current_value)
        
        # Show text entry, hide combo
        self.alt_text_entry.pack(fill=tk.X, pady=2)
        self.alt_value_combo.pack_forget()
        
        # Show the alternative value frame
        self.alt_value_frame.pack(fill=tk.X, padx=5, pady=5, in_=self.step_validation_frame)
        
        # Focus on text entry for immediate editing
        self.alt_text_entry.focus_set()
        self.alt_text_entry.select_range(0, tk.END)
        
        self.log(f"  → Enter the correct value for text field {field_id}")
        self.log(f"    Current value: '{current_value}'")
    
    def apply_alternative_value(self):
        """Apply the selected alternative value"""
        if not self.step_mode:
            return
        
        step_data = self.step_tests[self.current_step]
        field_id = step_data[0]
        field_type = step_data[3]
        
        if field_type == 'btn':
            # Handle button field correction
            selected_value = self.alt_value_var.get()
            if not selected_value:
                messagebox.showwarning("Warning", "Please select a value first.")
                return
            
            # Get the PDF value for the selected display value
            field_info = self.field_mapping[field_id]
            values = field_info.get('values', {})
            pdf_value = values.get(selected_value)
            
            if pdf_value is not None:
                # Apply the alternative value
                success = self.set_button_field(field_id, pdf_value)
                if success:
                    # Mark as correct with the alternative value
                    self.step_results[self.current_step] = {
                        'result': 'corrected',
                        'original_value': step_data[4] if len(step_data) > 4 else "Unknown",
                        'correct_value': selected_value
                    }
                    
                    self.log(f"  ✓ Applied alternative button value '{selected_value}' and marked as CORRECTED")
                    
                    # Refresh display
                    self.display_pdf_page()
                    self.populate_field_list()
                    
                    # Hide alternative value selection
                    self.alt_value_frame.pack_forget()
                    
                    # Auto-advance to next step
                    self.next_step()
                else:
                    self.log(f"  ✗ Failed to apply alternative button value")
            else:
                self.log(f"  ✗ Invalid alternative button value selected")
                
        elif field_type == 'text':
            # Handle text field correction
            new_text_value = self.alt_text_var.get()
            if not new_text_value.strip():
                messagebox.showwarning("Warning", "Please enter a value first.")
                return
            
            # Apply the alternative text value
            success = self.set_text_field(field_id, new_text_value)
            if success:
                # Mark as correct with the alternative value
                self.step_results[self.current_step] = {
                    'result': 'corrected',
                    'original_value': step_data[1],
                    'correct_value': new_text_value
                }
                
                self.log(f"  ✓ Applied alternative text value '{new_text_value}' and marked as CORRECTED")
                
                # Refresh display
                self.display_pdf_page()
                self.populate_field_list()
                
                # Hide alternative value selection
                self.alt_value_frame.pack_forget()
                
                # Auto-advance to next step
                self.next_step()
            else:
                self.log(f"  ✗ Failed to apply alternative text value")
    
    def show_test_results_summary(self):
        """Show summary of test results"""
        if not self.step_results:
            return
        
        correct = sum(1 for r in self.step_results.values() if r['result'] == 'correct')
        no_change = sum(1 for r in self.step_results.values() if r['result'] == 'no_change')
        different_field = sum(1 for r in self.step_results.values() if r['result'] == 'different_field')
        skipped = sum(1 for r in self.step_results.values() if r['result'] == 'skip')
        total = len(self.step_results)
        
        summary = f"""
Test Results Summary:
✓ Correct: {correct}
✗ No Change: {no_change}
⚠ Different Field: {different_field}
? Skipped: {skipped}
Total tested: {total}/{len(self.step_tests)}

Working Fields: {correct}/{total} ({(correct / total * 100):.1f}%)
"""
        
        self.log(summary)
        
        # Show detailed issues
        issues = []
        for step_idx, result in self.step_results.items():
            if result['result'] == 'different_field':
                step_data = self.step_tests[step_idx]
                field_id = step_data[0]
                actual_field = result.get('actual_field', 'none')
                issues.append(f"Field {field_id} → targets field {actual_field}")
        
        if issues:
            self.log("\nField mapping issues:")
            for issue in issues:
                self.log(f"  {issue}")
        
        # Save results to file
        self.save_validation_results()
    
    def save_validation_results(self):
        """Save validation results to JSON file"""
        if not self.step_results:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"validation_results_{timestamp}.json"
        
        # Prepare detailed results
        detailed_results = {
            'summary': {
                'total_steps': len(self.step_tests),
                'tested_steps': len(self.step_results),
                'correct': sum(1 for r in self.step_results.values() if r['result'] == 'correct'),
                'no_change': sum(1 for r in self.step_results.values() if r['result'] == 'no_change'),
                'different_field': sum(1 for r in self.step_results.values() if r['result'] == 'different_field'),
                'skipped': sum(1 for r in self.step_results.values() if r['result'] == 'skip'),
                'timestamp': timestamp
            },
            'field_tests': []
        }
        
        # Add detailed field test results
        for step_idx, result in self.step_results.items():
            if step_idx < len(self.step_tests):
                step_data = self.step_tests[step_idx]
                field_test = {
                    'step': step_idx + 1,
                    'field_id': step_data[0],
                    'field_name': self.field_mapping.get(step_data[0], {}).get('name', 'Unknown'),
                    'field_type': step_data[3],
                    'test_description': step_data[2],
                    'validation_result': result['result']
                }
                
                # Add specific details based on result type
                if result['result'] == 'corrected':
                    field_test['original_value'] = result['original_value']
                    field_test['correct_value'] = result['correct_value']
                elif step_data[3] == 'btn' and len(step_data) > 4:
                    field_test['tested_value'] = step_data[4]
                elif step_data[3] == 'text':
                    field_test['tested_value'] = step_data[1]
                
                detailed_results['field_tests'].append(field_test)
        
        # Save to file
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_results, f, indent=2, ensure_ascii=False)
            
            self.log(f"\nValidation results saved to: {results_file}")
            
        except Exception as e:
            self.log(f"Error saving validation results: {e}")
    
    def __del__(self):
        """Cleanup"""
        if self.current_doc:
            self.current_doc.close()
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            os.remove(self.temp_pdf_path)

def main():
    root = tk.Tk()
    app = PDFFormGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 