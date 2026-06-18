# Requirements Gathering Case Study

This document is a stakeholder interview scenario for students to practice
requirements gathering before designing a data engineering system.

The goal is not only to identify what the stakeholder asks for, but also to
separate symptoms, business needs, technical constraints, open questions, and
possible data architecture decisions.

## Scenario

A new data engineer joins a company and meets with a data scientist who supports
the marketing team. The marketing team wants fresher product sales analytics by
region and eventually more personalized product recommendations for customers
browsing the sales platform.

At the moment, the data scientist receives a manual data dump once per day from
the software engineering team. The production database contains the source sales
data, but the software team does not want to provide direct access because of
operational risk.

## Stakeholder Interview

**Data engineer:** Hi, I'm Joe, and I just joined this week as a new data
engineer. I'm excited to get started working on data projects with you. I
thought it would be great if we could discuss what you're working on and how I
can help.

**Data scientist:** Yeah, absolutely. It's great to meet you and have you at the
company. I started here as a data scientist a few months ago, and it has been
hectic to say the least.

**Data engineer:** Hectic? Tell me more.

**Data scientist:** Our marketing team is asking for real-time analysis of
product sales by region. They want to look at which products customers bought,
where customers are located, and other sales behavior.

Right now, all product sales data is located in the production database for our
sales platform. The software engineering team does not want to give me direct
access because they are worried I might break something. Because of that, they
give me a data dump once a day, and I manually pull it.

**Data engineer:** So you are getting the information you need, but the process
is cumbersome because you need to download it manually.

**Data scientist:** I guess I am getting the information, but I am also getting
a lot of data I do not need. Around 90% of the dump is unnecessary for my work.
The data is stored across CSV and JSON files. I need to run a series of
processing steps to extract what I need from each file, clean it, aggregate it,
and save it in a format I can use for dashboards.

**Data engineer:** It sounds like you are spending a lot of time processing the
data before you can use it for analytics.

**Data scientist:** Yes. I probably spend around 80% of my time cleaning and
processing data.

Often my processing scripts crash because there are anomalies or unexpected
entries in the files from the software team. A few times the software team
changed the format of the data dump, and I only found out when my scripts stopped
running. Then I had to refactor everything to work with the new format.

It is not uncommon for me to spend an entire day getting the data into a usable
format for the dashboards. Meanwhile, the marketing team wants regional sales
analytics in real time. By the time I push updates, the information is often
already two days old.

**Data engineer:** That sounds painful. If I understand correctly, there are two
major problems. First, you only receive data dumps once per day. Second, the data
cleaning and processing steps are manual, laborious, and unpredictable.

**Data scientist:** Exactly. Under the current process, I do not see how I can
deliver faster results. Marketing wants current metrics, not numbers that are
two days old.

**Data engineer:** You mentioned that marketing wants real-time updates. What
are they hoping to do with that information?

**Data scientist:** They are focused on understanding the effectiveness of their
marketing campaigns and observing short-term and long-term trends in product
sales so they can time campaigns better.

We have also been working on a recommendation engine for the website that
suggests products to customers when they browse or make a purchase.

**Data engineer:** So there are a few distinct use cases. Right now, you provide
dashboards and a recommendation engine that address some of these needs.

**Data scientist:** Yes and no.

For dashboards, I show product sales by category and region over the past 30
days. The dashboard includes 30-day totals and timeline plots with daily
numbers. Marketing requested that so they can see broad trends from region to
region.

They can also drill into a region to see a finer breakdown by individual product
or by a smaller time cadence, like hourly instead of daily. But the data is
usually at least two days old, so it does not show current numbers.

For the recommender, I am currently analyzing which products have been most
popular over the past week. I pass those product IDs to the software team so they
can recommend popular products to everyone browsing the website.

It is not customized to individual customers yet. It just shows popular
products.

I am working on training a model to do personalized recommendations using a
content-based filtering method, but nothing has been deployed yet.

**Data engineer:** For the recommendation system, it sounds like you need more
data for training. Once a model is ready to deploy, you will need a system that
sends user activity data from the sales platform to the model and sends product
recommendations back to the platform while the user is browsing.

**Data scientist:** Yes, that is the plan. Like any ecommerce website or app,
when users browse, add items to cart, or make purchases, they should see product
recommendations based on what they have been looking at or buying.

**Data engineer:** For the dashboards, you said marketing wants current data.
Do you know what actions they hope to take based on current data that they
cannot take with data that is two days old?

**Data scientist:** They have talked about targeting ad campaigns based on
current data. That might mean looking at what customers are doing right now in
terms of purchases or other sales platform activity.

But I am not sure whether they need to know what customers are doing this second,
within the past hour, or just today instead of yesterday.

**Data engineer:** That is helpful. I can follow up with marketing to understand
what actions they want to take. If we know the action, we can decide how much
latency the system can tolerate.

**Data scientist:** That makes sense. Let me know if there is anything else I
can do to help.

**Data engineer:** This has been helpful. If I understand correctly, it would
help if we could create a more direct and timely ingestion process from the
database where sales are recorded.

Then we need to automate and orchestrate the transformation and serving of that
data into the format you need for dashboards and recommendations.

**Data scientist:** Yes, definitely. If ingestion and processing could be
handled automatically and stored in the format I need, it would make my life much
easier and let me focus on analysis.

**Data engineer:** Great. A good next step is to check with the marketing team
to better understand their needs.
