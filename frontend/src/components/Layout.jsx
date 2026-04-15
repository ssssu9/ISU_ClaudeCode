import { Link, useLocation } from 'react-router-dom'

export default function Layout({ children }) {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-lg font-bold text-indigo-600">
          🧾 영수증 지출 관리
        </Link>
        <nav className="flex gap-4">
          <Link
            to="/"
            className={`text-sm font-medium ${pathname === '/' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-900'}`}
          >
            대시보드
          </Link>
          <Link
            to="/upload"
            className={`text-sm font-medium ${pathname === '/upload' ? 'text-indigo-600' : 'text-gray-500 hover:text-gray-900'}`}
          >
            업로드
          </Link>
        </nav>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-6">
        {children}
      </main>

      <footer className="text-center text-xs text-gray-400 py-4 border-t border-gray-100">
        Receipt Expense Tracker
      </footer>
    </div>
  )
}
