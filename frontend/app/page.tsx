import ActionButton from "@/components/ActionButton";
import FeatureCard from "@/components/FeatureCard";

const actions = [
  {
    text: "Upload Tickets",
  },
  {
    text: "View Dashboard",
  },
  {
    text: "Ask AI",
  }
]

const features = [

{
 title:"AI Ticket Classification",
 description:
 "Automatically classify customer support tickets."
},

{
 title:"Priority Detection",
 description:
 "Identify high priority customer issues."
},

{
 title:"Customer Insights",
 description:
 "Discover support trends using AI."
}

];



export default function Home() {
  return (
    <main>
      <h1>
        SupportLens
      </h1>

      <p>
        AI Customer Support Analytics Platform
      </p>
      <div>

        {
          actions.map((action) => (
            <ActionButton
              key={action.text}
              text={action.text}
            />
          ))
        }

      </div>

      <div>

      {
      features.map((feature)=>(
      <FeatureCard
        key={feature.title}
        title={feature.title}
        description={feature.description}
      />
      ))
      }

      </div>
      
          </main>
  );
}