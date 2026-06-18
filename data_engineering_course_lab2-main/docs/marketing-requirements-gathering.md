# Marketing Requirements Gathering Case Study

This document is a stakeholder interview scenario between a newly hired data
engineer and a product marketing manager. It helps students practice translating
business actions into data freshness, dashboard, and recommendation system
requirements.

The marketing conversation is especially useful because it clarifies what "real
time" means for the business. In this case, marketing does not necessarily need
second-by-second dashboards. They need data fresh enough to act while product
demand is still rising.

## Scenario

The company has two marketing-driven data initiatives:

- Product sales dashboards by category, region, product, and time.
- A product recommendation system for the ecommerce platform.

These initiatives support larger business goals:

- Launch new products by understanding market trends.
- Improve customer retention by recommending products that match customer
  preferences.
- Help marketing respond quickly when demand spikes in a region or product
  category.

## Requirements Gathering Frame

During requirements gathering, the data engineer should look for four things:

1. What system or solution currently exists?
2. What problems exist with the current system or data?
3. What actions does the stakeholder plan to take with the data?
4. Which other stakeholders or follow-up conversations are needed?

## Stakeholder Interview

**Data engineer:** Hi Colleen. I'm Joe, the new data engineer hired at the
company.

**Product marketing manager:** Hi Joe. I'm excited to have you here.

**Data engineer:** Great to meet you. I've been talking to people around the
company to better understand our data needs. I'm putting together requirements
for the data systems I will be working on.

**Product marketing manager:** Definitely. We have been thinking a lot lately
about how we can use data to make more informed decisions and drive the metrics
we care about on the marketing team. We are really looking forward to having you
work on this.

**Data engineer:** In my conversation with the data scientists, I learned that
they have been working on two initiatives with you: dashboards for product sales
metrics and a product recommendation engine. Is that right?

**Product marketing manager:** That's correct. Both initiatives are in a
prototype state, and we would like to improve both of them.

**Data engineer:** Could you first tell me more about the current state of the
systems, so I can understand where we are now?

**Product marketing manager:** For the dashboards, what we have now is
essentially what we want in terms of how metrics and trends are displayed. The
problem is that there is usually a lag of a couple of days between when a new
sale is recorded and when we can see it in the dashboards.

Our data scientist created dashboards where we can see product sales by category
and region, with time plots showing daily numbers. That helps us see broad
trends from region to region.

We can also drill into a particular region to see details by individual product
or by a more granular time cadence, like hourly instead of daily.

All of that is useful, but we want to see it in real time rather than when the
data is already two days old.

**Data engineer:** It sounds like the dashboards are already valuable for
monitoring long-term trends, but there are things you want to do that require
more recent data.

**Product marketing manager:** That's right. In addition to monitoring long-term
metrics, we want to see in real time when a particular product is trending.

If we can see that happening, we can try to capture the momentum and push more
targeted promotional campaigns focused on a specific region and product.

Right now, we occasionally see interesting regional demand spikes for particular
products. We would like to know about those spikes when they are actually
happening, not after demand has already subsided.

**Data engineer:** Tell me more about these demand spikes. What do they look
like, and how long do they usually last?

**Product marketing manager:** In many cases, demand rises sharply over a span of
a few hours and then eventually drops off again. Sometimes it lasts a day or two,
but sometimes it drops more quickly in just a few hours.

**Data engineer:** If I understand correctly, you want to observe one of these
spikes while it is happening so you can take action based on that information.

**Product marketing manager:** That's right. If we see sales ticking up steadily
for two or three hours in a row, we could have a plan in place to take immediate
action and push out targeted promotions.

**Data engineer:** If your dashboard reflected product sales from one hour ago
instead of two days ago, would that be fresh enough for you to take action?

**Product marketing manager:** Yes. Data that is only one hour old would be
great.

**Data engineer:** That helps me understand the dashboard need. I would also
like to learn more about the recommendation system. Do you have something
working already?

**Product marketing manager:** Sort of. We asked the data scientists to identify
the most popular products from the previous week of sales. Then the platform team
serves those products as recommendations to everyone at checkout.

It is more like a "popular products of the week" feature than a personalized
recommendation system.

**Data engineer:** So you have a basic recommender, but it is not personalized.
You would like something that considers a customer's purchase history and what
they have in their cart so it can make customized recommendations.

**Product marketing manager:** Yes, exactly. Like other ecommerce platforms,
while customers are shopping or checking out, they should see recommendations
for products they might be interested in.

**Data engineer:** Great. This conversation has been helpful for understanding
what you need from the dashboards and recommendation system. I will probably
have more questions as we start building, and I will let you know when we have
something ready to test.

**Product marketing manager:** Awesome. Thank you. I look forward to seeing what
you build, and feel free to reach out any time.
