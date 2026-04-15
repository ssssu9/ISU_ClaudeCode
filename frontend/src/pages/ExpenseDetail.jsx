import { useParams } from 'react-router-dom'

export default function ExpenseDetail() {
  const { id } = useParams()

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">지출 상세</h1>
      <p className="text-gray-500 text-sm">ID: {id}</p>
      {/* TODO: ReceiptImage, EditForm */}
    </div>
  )
}
