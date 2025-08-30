# GR24 Mac Build Instructions

এই guide টি আপনাকে Windows থেকে Mac এর জন্য executable build করতে সাহায্য করবে।

## 🎯 লক্ষ্য
Mac user রা যাতে কোন কিছু install না করেই আপনার application ব্যবহার করতে পারে।

## 📋 প্রয়োজনীয়তা

### পদ্ধতি 1: Docker (সবচেয়ে সহজ)
- Docker Desktop installed
- Internet connection

### পদ্ধতি 2: GitHub Actions (সবচেয়ে সুবিধাজনক)
- Git installed
- GitHub account
- Internet connection

### পদ্ধতি 3: Manual
- Mac computer access
- Python 3.11 on Mac

## 🚀 Quick Start

### পদ্ধতি 1: Docker দিয়ে Build

1. **Docker Desktop Install করুন:**
   - https://www.docker.com/products/docker-desktop থেকে download করুন
   - Install করুন এবং restart করুন

2. **Build Script চালান:**
   ```bash
   python build_mac_windows.py
   ```
   
3. **Option 1 নির্বাচন করুন** (Docker)

4. **Build complete হলে** `./dist/GR24_Mac` file টি Mac user দের দিতে পারেন

### পদ্ধতি 2: GitHub Actions দিয়ে Build (Recommended)

1. **Git Install করুন:**
   - https://git-scm.com/ থেকে download করুন

2. **GitHub repository তৈরি করুন:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

3. **Build Script চালান:**
   ```bash
   python build_mac_windows.py
   ```
   
4. **Option 2 নির্বাচন করুন** (GitHub Actions)

5. **Code push করুন:**
   ```bash
   git add .
   git commit -m "Add Mac build workflow"
   git push
   ```

6. **GitHub এ যান:**
   - Actions tab এ build progress দেখুন
   - Releases section থেকে executable download করুন

## 📱 Mac User Instructions

Mac user রা এই steps follow করবে:

1. **GR24_Mac file download করুন**

2. **File open করুন:**
   - Right-click on GR24_Mac
   - Select "Open"
   - Click "Open" in the dialog

3. **Security warning এ:**
   - System Preferences > Security & Privacy এ যান
   - "Open Anyway" button click করুন

4. **Application use করুন!**

## 🔧 Troubleshooting

### Docker Issues:
- Docker Desktop running আছে কিনা check করুন
- Windows Subsystem for Linux (WSL2) enabled আছে কিনা check করুন

### GitHub Actions Issues:
- Repository public আছে কিনা check করুন
- GitHub Actions enabled আছে কিনা check করুন

### Mac Security Issues:
- Gatekeeper settings check করুন
- Developer tools allow করুন

## 📁 File Structure

```
GR24_MAC/
├── mac.py                    # Main application
├── build_mac_windows.py      # Build script
├── requirements.txt          # Python dependencies
├── .github/workflows/        # GitHub Actions
│   └── build-mac.yml
└── dist/                     # Output directory
    └── GR24_Mac             # Mac executable
```

## 🎉 Features

✅ **No Installation Required** - Mac user রা শুধু file download করে use করতে পারবে

✅ **Cross-platform Build** - Windows থেকে Mac executable তৈরি

✅ **Automatic Updates** - GitHub Actions দিয়ে automatic build

✅ **Professional Packaging** - Clean, standalone executable

## 📞 Support

যদি কোন সমস্যা হয়:
1. Error messages check করুন
2. Dependencies installed আছে কিনা verify করুন
3. Internet connection check করুন

## 🔄 Update Process

নতুন version release করার জন্য:
1. Code update করুন
2. Git push করুন
3. GitHub Actions automatically build করবে
4. New release download করুন

---

**Note:** এই process টি Mac user রা কোন technical knowledge ছাড়াই ব্যবহার করতে পারবে!
