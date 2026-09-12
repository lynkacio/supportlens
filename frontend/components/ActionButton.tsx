interface ActionButtonProps {
  text: string;
  variant?: "primary" | "secondary";
}

export default function ActionButton({
  text,
  variant = "primary",
}: ActionButtonProps) {

  return (
    <button
      className={
        variant === "primary"
        ? "px-6 py-3 bg-blue-600 text-white rounded-lg"
        : "px-6 py-3 bg-gray-200 rounded-lg"
      }
    >      
    {text}
    </button>
  );

}