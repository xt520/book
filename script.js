// 初始化 Materialize 组件
document.addEventListener('DOMContentLoaded', function () {
    M.Modal.init(document.querySelectorAll('.modal'), {
        onCloseEnd: () => App.stopScan()
    });
    M.FormSelect.init(document.querySelectorAll('select'));
    App.init();
});

const App = {
    books: [],
    deleteTargetId: null,
    currentFilter: 'all',
    currentSort: 'newest',
    html5QrCode: null,

    init() {
        this.loadBooks();
        this.updateDashboard();
        this.render();
        this.initEvents();
    },

    loadBooks() {
        const data = localStorage.getItem('enterprise_books');
        this.books = data ? JSON.parse(data) : [];
    },

    saveBooks() {
        localStorage.setItem('enterprise_books', JSON.stringify(this.books));
        this.updateDashboard();
    },

    updateDashboard() {
        document.getElementById('total-count').innerText = this.books.length;

        const borrowedCount = this.books.filter(b => b.borrowedBy).length;
        document.getElementById('borrowed-count').innerText = borrowedCount;

        const categories = new Set(this.books.map(b => b.category));
        document.getElementById('category-count').innerText = categories.size;

        const authors = new Set(this.books.map(b => b.author));
        document.getElementById('author-count').innerText = authors.size;

        this.renderCategoryFilters(categories);
    },

    renderCategoryFilters(categories) {
        const filterContainer = document.getElementById('category-filters');
        const currentActive = this.currentFilter;

        let html = `<div class="chip ${currentActive === 'all' ? 'active-chip white-text' : 'clickable'}" data-filter="all">全部</div>`;

        Array.from(categories).sort().forEach(cat => {
            html += `<div class="chip ${currentActive === cat ? 'active-chip white-text' : 'clickable'}" data-filter="${cat}">${cat}</div>`;
        });

        filterContainer.innerHTML = html;

        // 绑定点击事件
        filterContainer.querySelectorAll('.chip').forEach(chip => {
            chip.onclick = () => {
                this.currentFilter = chip.getAttribute('data-filter');
                this.render(document.getElementById('search-input').value);
                this.renderCategoryFilters(categories);
            };
        });
    },

    render(filterTerm = '') {
        const container = document.getElementById('book-container');
        const emptyState = document.getElementById('empty-state');
        container.innerHTML = '';

        // 1. 过滤
        let displayList = this.books.filter(book => {
            const matchesSearch = book.title.toLowerCase().includes(filterTerm.toLowerCase()) ||
                book.author.toLowerCase().includes(filterTerm.toLowerCase()) ||
                book.isbn.includes(filterTerm);
            const matchesCategory = this.currentFilter === 'all' || book.category === this.currentFilter;
            return matchesSearch && matchesCategory;
        });

        // 2. 排序
        if (this.currentSort === 'title') {
            displayList.sort((a, b) => a.title.localeCompare(b.title, 'zh'));
        } else if (this.currentSort === 'category') {
            displayList.sort((a, b) => a.category.localeCompare(b.category, 'zh'));
        } else {
            displayList.sort((a, b) => b.id - a.id); // 最新优先
        }

        if (displayList.length === 0) {
            emptyState.classList.remove('hide');
        } else {
            emptyState.classList.add('hide');
            displayList.forEach(book => {
                const statusBadge = book.borrowedBy
                    ? `<span class="new badge red left" data-badge-caption="已借出: ${book.borrowedBy}"></span>`
                    : `<span class="new badge green left" data-badge-caption="在库"></span>`;

                const actionButtons = book.borrowedBy
                    ? `<a href="#!" onclick="App.returnBook('${book.id}')" class="blue-text"><i class="material-icons left">assignment_return</i>归还</a>`
                    : `<a href="#!" onclick="App.openBorrowModal('${book.id}', '${book.title}')" class="blue-text"><i class="material-icons left">assignment_ind</i>借阅</a>`;

                const card = `
                    <div class="col s12 m6 l4">
                        <div class="card book-card hoverable">
                            <div class="card-content">
                                <span class="category-chip indigo lighten-5 indigo-text">${book.category}</span>
                                ${statusBadge}
                                <div style="clear:both; padding-top:10px"></div>
                                <span class="card-title indigo-text text-darken-2">${book.title}</span>
                                <div class="book-info">
                                    <p><i class="material-icons">person</i> ${book.author}</p>
                                    <p><i class="material-icons">fingerprint</i> ISBN: ${book.isbn}</p>
                                </div>
                            </div>
                            <div class="card-action">
                                ${actionButtons}
                                <a href="#!" onclick="App.openEditModal('${book.id}')" class="indigo-text"><i class="material-icons left">edit</i>编辑</a>
                                <a href="#!" onclick="App.confirmDelete('${book.id}', '${book.title}')" class="red-text"><i class="material-icons left">delete</i>删除</a>
                            </div>
                        </div>
                    </div>
                `;
                container.innerHTML += card;
            });
        }
    },

    initEvents() {
        document.getElementById('book-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit();
        });

        document.getElementById('search-input').addEventListener('input', (e) => {
            this.render(e.target.value);
        });

        document.getElementById('sort-select').onchange = (e) => {
            this.currentSort = e.target.value;
            this.render(document.getElementById('search-input').value);
        };

        document.getElementById('confirm-delete-btn').addEventListener('click', () => {
            this.deleteBook(this.deleteTargetId);
        });

        document.getElementById('borrow-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleBorrowSubmit();
        });

        document.getElementById('isbn').addEventListener('blur', (e) => {
            const isbn = e.target.value.trim();
            if (isbn && !document.getElementById('title').value) {
                this.fetchBookInfo(isbn);
            }
        });

        // 摄像头扫码功能
        document.getElementById('scan-btn').onclick = () => {
            this.startScan();
        };

        // 图片扫码功能
        document.getElementById('scan-image-btn').onclick = () => {
            document.getElementById('isbn-image-input').click();
        };

        document.getElementById('isbn-image-input').onchange = (e) => {
            this.scanImageFile(e.target.files[0]);
        };

        // 导出功能
        document.getElementById('export-btn').onclick = () => {
            const blob = new Blob([JSON.stringify(this.books, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `图书备份_${new Date().toLocaleDateString()}.json`;
            a.click();
            M.toast({ html: '备份文件已导出', classes: 'blue' });
        };

        // 导入功能
        const importInput = document.getElementById('import-input');
        document.getElementById('import-trigger').onclick = () => importInput.click();
        importInput.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const imported = JSON.parse(event.target.result);
                    if (Array.isArray(imported)) {
                        this.books = imported;
                        this.saveBooks();
                        this.render();
                        M.toast({ html: '数据恢复成功！', classes: 'green' });
                    }
                } catch (err) {
                    M.toast({ html: '导入失败：无效的文件格式', classes: 'red' });
                }
            };
            reader.readAsText(file);
        };
    },

    handleFormSubmit() {
        const id = document.getElementById('edit-id').value;
        const title = document.getElementById('title').value;
        const author = document.getElementById('author').value;
        const isbn = document.getElementById('isbn').value;
        const category = document.getElementById('category').value;

        const duplicate = this.books.find(b => b.isbn === isbn && b.id !== id);
        if (duplicate) {
            M.toast({ html: '错误：ISBN 编号已存在！', classes: 'red darken-2' });
            return;
        }

        if (id) {
            const index = this.books.findIndex(b => b.id === id);
            const currentBook = this.books[index];
            this.books[index] = { ...currentBook, title, author, isbn, category };
            M.toast({ html: '更新成功', classes: 'green' });
        } else {
            this.books.push({ id: Date.now().toString(), title, author, isbn, category });
            M.toast({ html: '已入库', classes: 'green' });
        }

        this.saveBooks();
        this.render();
        M.Modal.getInstance(document.getElementById('book-modal')).close();
        this.resetForm();
    },

    confirmDelete(id, title) {
        this.deleteTargetId = id;
        document.getElementById('delete-book-title').innerText = title;
        M.Modal.getInstance(document.getElementById('delete-modal')).open();
    },

    deleteBook(id) {
        this.books = this.books.filter(b => b.id !== id);
        this.saveBooks();
        this.render();
        M.toast({ html: '已删除', classes: 'orange darken-3' });
    },

    openEditModal(id) {
        const book = this.books.find(b => b.id === id);
        if (book) {
            document.getElementById('edit-id').value = book.id;
            document.getElementById('title').value = book.title;
            document.getElementById('author').value = book.author;
            document.getElementById('isbn').value = book.isbn;
            document.getElementById('category').value = book.category;
            document.getElementById('modal-title').innerText = '编辑图书信息';
            M.updateTextFields();
            M.FormSelect.init(document.querySelectorAll('select'));
            M.Modal.getInstance(document.getElementById('book-modal')).open();
        }
    },

    resetForm() {
        document.getElementById('book-form').reset();
        document.getElementById('edit-id').value = '';
        M.FormSelect.init(document.querySelectorAll('select'));
    },

    openBorrowModal(id, title) {
        document.getElementById('borrow-book-id').value = id;
        document.getElementById('borrow-book-title').innerText = title;
        document.getElementById('borrower-name').value = '';
        M.updateTextFields();
        M.Modal.getInstance(document.getElementById('borrow-modal')).open();
    },

    handleBorrowSubmit() {
        const id = document.getElementById('borrow-book-id').value;
        const name = document.getElementById('borrower-name').value;

        const index = this.books.findIndex(b => b.id === id);
        if (index !== -1) {
            this.books[index].borrowedBy = name;
            this.saveBooks();
            this.render();
            M.Modal.getInstance(document.getElementById('borrow-modal')).close();
            M.toast({ html: `图书已借给 ${name}`, classes: 'blue' });
        }
    },

    returnBook(id) {
        const index = this.books.findIndex(b => b.id === id);
        if (index !== -1) {
            const name = this.books[index].borrowedBy;
            delete this.books[index].borrowedBy;
            this.saveBooks();
            this.render();
            M.toast({ html: `已收回 ${name} 借阅的图书`, classes: 'green' });
        }
    },

    startScan() {
        const reader = document.getElementById('reader');
        reader.style.display = 'block';

        if (!this.html5QrCode) {
            this.html5QrCode = new Html5Qrcode("reader");
        }

        this.html5QrCode.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: { width: 250, height: 150 } },
            (decodedText) => {
                document.getElementById('isbn').value = decodedText;
                M.updateTextFields();
                M.toast({ html: '扫码成功，正在查询图书信息...', classes: 'green' });
                this.fetchBookInfo(decodedText);
                this.stopScan();
            },
            (errorMessage) => {
                // 忽略扫描过程中的普通反馈
            }
        ).catch(err => {
            console.error(err);
            let msg = '无法启动摄像头。';
            if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
                msg = '由于安全限制，非 HTTPS 环境无法在手机上调用摄像头。请使用电脑访问或开启 HTTPS。';
            }
            M.toast({ html: msg, classes: 'red', displayLength: 6000 });
            reader.style.display = 'none';
        });
    },

    async fetchBookInfo(isbn) {
        if (!isbn) return;

        // 清理 ISBN 格式 (只保留数字和 X)
        const cleanIsbn = isbn.toString().toUpperCase().replace(/[^0-9X]/g, '');

        if (cleanIsbn.length < 10) return;

        try {
            // 显示加载中的状态
            M.toast({ html: '正在联网查询图书详情...', classes: 'blue' });

            // 使用 Open Library API 作为主要数据源 (免费、无需 Key)
            const response = await fetch(`https://openlibrary.org/api/books?bibkeys=ISBN:${cleanIsbn}&format=json&jscmd=data`);
            const data = await response.json();
            const bookKey = `ISBN:${cleanIsbn}`;

            if (data[bookKey]) {
                const info = data[bookKey];

                // 只有当字段为空时才自动填充，或者是由扫码触发的
                const titleField = document.getElementById('title');
                const authorField = document.getElementById('author');

                titleField.value = info.title || titleField.value;
                if (info.authors) {
                    authorField.value = info.authors.map(a => a.name).join(', ');
                }

                // 尝试匹配类别
                if (info.subjects) {
                    const subjects = info.subjects.map(s => s.name).join(' ').toLowerCase();
                    const categorySelect = document.getElementById('category');
                    if (subjects.includes('computer') || subjects.includes('program') || subjects.includes('technology')) {
                        categorySelect.value = '编程';
                    } else if (subjects.includes('fiction') || subjects.includes('literature')) {
                        categorySelect.value = '文学';
                    } else if (subjects.includes('science') || subjects.includes('physics') || subjects.includes('math')) {
                        categorySelect.value = '科技';
                    } else if (subjects.includes('art') || subjects.includes('design')) {
                        categorySelect.value = '艺术';
                    } else {
                        categorySelect.value = '其它';
                    }
                }

                M.updateTextFields();
                M.FormSelect.init(document.querySelectorAll('select'));
                M.toast({ html: '图书信息填充成功', classes: 'green' });
            } else {
                // 如果 Open Library 没搜到，尝试 Google Books API
                const gResp = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${cleanIsbn}`);
                const gData = await gResp.json();

                if (gData.items && gData.items.length > 0) {
                    const volumeInfo = gData.items[0].volumeInfo;
                    document.getElementById('title').value = volumeInfo.title || document.getElementById('title').value;
                    if (volumeInfo.authors) {
                        document.getElementById('author').value = volumeInfo.authors.join(', ');
                    }
                    M.updateTextFields();
                    M.toast({ html: '从 Google Books 自动填充信息', classes: 'green' });
                } else {
                    M.toast({ html: '未查到详情，请手动输入', classes: 'orange' });
                }
            }
        } catch (error) {
            console.error('Fetch error:', error);
            M.toast({ html: '联网获取信息失败', classes: 'red' });
        }
    },

    stopScan() {
        if (this.html5QrCode && this.html5QrCode.isScanning) {
            this.html5QrCode.stop().then(() => {
                document.getElementById('reader').style.display = 'none';
            }).catch(err => console.error(err));
        } else {
            const reader = document.getElementById('reader');
            if (reader) reader.style.display = 'none';
        }
    },

    async scanImageFile(file) {
        if (!file) return;

        const imagePreview = document.getElementById('image-preview');
        const previewImg = document.getElementById('scan-preview-img');
        const loadingIndicator = document.getElementById('scan-loading');

        // 显示图片预览
        const imageUrl = URL.createObjectURL(file);
        previewImg.src = imageUrl;
        imagePreview.style.display = 'block';
        loadingIndicator.style.display = 'block';

        try {
            // 创建一个新的 Html5Qrcode 实例用于扫描文件
            const html5QrCode = new Html5Qrcode("image-preview");

            // 扫描图片文件
            const decodedText = await html5QrCode.scanFile(file, true);

            // 扫描成功
            document.getElementById('isbn').value = decodedText;
            M.updateTextFields();
            M.toast({ html: `识别成功: ${decodedText}`, classes: 'green' });

            // 自动获取图书信息
            this.fetchBookInfo(decodedText);

            // 清理
            loadingIndicator.style.display = 'none';

            // 2秒后隐藏预览
            setTimeout(() => {
                imagePreview.style.display = 'none';
                URL.revokeObjectURL(imageUrl);
            }, 2000);

        } catch (error) {
            console.error('图片扫描错误:', error);
            loadingIndicator.style.display = 'none';

            // 提供更详细的错误信息
            let errorMsg = '未能在图片中识别到条形码';
            if (error.includes && error.includes('No barcode')) {
                errorMsg = '图片中未发现条形码，请确保条形码清晰可见';
            } else if (error.includes && error.includes('Could not decode')) {
                errorMsg = '条形码无法解码，请尝试更清晰的图片';
            }

            M.toast({ html: errorMsg, classes: 'orange', displayLength: 4000 });

            // 3秒后隐藏预览
            setTimeout(() => {
                imagePreview.style.display = 'none';
                URL.revokeObjectURL(imageUrl);
            }, 3000);
        }

        // 重置文件输入，允许重新选择相同的文件
        document.getElementById('isbn-image-input').value = '';
    }
};
