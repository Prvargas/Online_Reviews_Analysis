# This file is used to create synthetic health care review data

from openai import OpenAI
import random
from datetime import datetime, timedelta
import pandas as pd
import os




##CLASS 1
import pandas as pd
import numpy as np

class CustomerDemographicTable:
    """
    A class to generate synthetic customer demographic data for Aetna's health care services.

    Attributes:
        n_customers (int): The number of synthetic customers to generate. Default is 1000.
        random_seed (int): The seed for random number generation to ensure reproducibility. Default is 42.
        aetna_service_states (list): List of states where Aetna provides services.
        aetna_service_states_to_region (dict): Dictionary mapping states to their respective regions.
        gender_distribution (list): List of possible gender categories.
        gender_probs (list): List of probabilities associated with each gender category.

    Methods:
        generate_data():
            Generates a synthetic customer demographic DataFrame.
    """

    def __init__(self, n_customers=1000, random_seed=42):
        """
        Initializes the CustomerDemographicTable with the given number of customers and random seed.

        Args:
            n_customers (int): Number of customers to generate.
            random_seed (int): Seed for random number generation.
        """
        self.n_customers = n_customers
        self.random_seed = random_seed
        self.aetna_service_states = [
            "Arizona", "California", "Delaware", "Florida", "Georgia", "Illinois",
            "Indiana", "Kansas", "Maryland", "Missouri", "North Carolina", "New Jersey",
            "Nevada", "Ohio", "Texas", "Utah", "Virginia"
        ]
        self.aetna_service_states_to_region = {
            "Illinois": "North", "Indiana": "North", "Kansas": "North", "Ohio": "North",
            "Arizona": "West", "California": "West", "Nevada": "West", "Utah": "West",
            "Delaware": "East", "Maryland": "East", "New Jersey": "East", "Virginia": "East",
            "Florida": "South", "Georgia": "South", "Missouri": "South", "North Carolina": "South", "Texas": "South"
        }
        self.gender_distribution = ["Female", "Male", "Other"]
        self.gender_probs = [0.55, 0.40, 0.05]

    def generate_data(self):
        """
        Generates a synthetic customer demographic DataFrame.

        The DataFrame contains the following columns:
        - Customer_ID: Unique identifier for each customer.
        - Plan_Type: Type of insurance plan ("Individual and Family" or "Medicare").
        - Age: Age of the customer, distributed based on the plan type.
        - Gender: Gender of the customer, chosen based on predefined probabilities.
        - State: State where the customer resides, chosen from Aetna service states.
        - Region: Region corresponding to the state.

        Returns:
            pd.DataFrame: A DataFrame containing the synthetic customer demographic data.
        """
        # Set random seed
        np.random.seed(self.random_seed)

        # Create the Customer_ID column
        customer_ids = np.arange(1, self.n_customers + 1)

        # Create the Plan_Type column
        plan_types = np.random.choice(["Individual and Family", "Medicare"], size=self.n_customers, p=[0.7, 0.3])

        # Create the Age column
        ages = np.where(
            plan_types == "Individual and Family",
            np.clip(np.random.normal(40, 10, self.n_customers), 25, 64),
            np.clip(np.random.gamma(2, 5, self.n_customers) + 60, 65, 80)  # using a gamma distribution which tends to produce a right-skewed distribution.
        )
        ages = np.round(ages).astype(int)

        # Create the Gender column
        genders = np.random.choice(self.gender_distribution, size=self.n_customers, p=self.gender_probs)

        # Create the State column
        states = np.random.choice(self.aetna_service_states, size=self.n_customers)

        # Create the Region column
        regions = [self.aetna_service_states_to_region[state] for state in states]

        # Create the DataFrame
        customer_df = pd.DataFrame({
            "Customer_ID": customer_ids,
            "Plan_Type": plan_types,
            "Age": ages,
            "Gender": genders,
            "State": states,
            "Region": regions
        })

        return customer_df







##CLASS 2
class SyntheticReviewGenerator:
    """
    SyntheticReviewGenerator generates synthetic customer reviews for a specified insurance company
    using the OpenAI API. The reviews are generated based on predefined prompts categorized by sentiment
    (positive, neutral, negative) and include ratings that follow a specified mean and standard deviation
    per year.

    Parameters:
    - api_key (str): Your OpenAI API key.
    - company_name (str): The name of the insurance company for which reviews are generated.
    - num_customers (int): The number of unique customers. Default is 5.
    - num_reviews (int): The number of reviews to generate. Default is 5.
    - start_date (str): The start date for the review date range in 'mm/dd/yyyy' format. Default is "1/1/2020".
    - end_date (str): The end date for the review date range in 'mm/dd/yyyy' format. Default is "6/16/2024".
    - rating_mean_dict (dict): A dictionary containing the desired mean rating score for each year.
      Default is {2020: 1.5, 2021: 1.9, 2022: 2.4, 2023: 3.1, 2024: 4.2}.
    - std_dev (float): The standard deviation for the rating scores. Default is 2.0.

    Methods:
    - generate_review(prompt): Generates a single review text using the OpenAI API based on the provided prompt.
    - generate_random_date(): Generates a random date within the specified date range.
    - generate_rating(year): Generates a rating for the given year based on the mean rating and standard deviation.
    - generate_reviews(): Generates synthetic reviews and returns them as a pandas DataFrame.
    - save_to_csv(df, filename): Saves the DataFrame of reviews to a CSV file.

    Usage example:
    >>> api_key = "your-api-key"
    >>> rating_mean_dict = {2020: 1.5, 2021: 1.9, 2022: 2.4, 2023: 3.1, 2024: 4.2}
    >>> std_dev = 2.0
    >>> generator = SyntheticReviewGenerator(api_key, "Aetna's health insurance service", num_customers=5, num_reviews=5, start_date="1/1/2020", end_date="6/16/2024", rating_mean_dict=rating_mean_dict, std_dev=std_dev)
    >>> reviews_df = generator.generate_reviews()
    >>> generator.save_to_csv(reviews_df, 'synthetic_reviews_data.csv')
    >>> print(reviews_df.head())
    """

    def __init__(self, api_key, company_name, num_customers=5, num_reviews=5, start_date="1/1/2020", end_date="6/16/2024", rating_mean_dict=None, std_dev=2.0):
        # Initialize the OpenAI client with the provided API key
        self.client = OpenAI(api_key=api_key)
        # Set the company name for which reviews will be generated
        self.company_name = company_name
        # Set the number of customers and reviews to generate
        self.num_customers = num_customers
        self.num_reviews = num_reviews
        # Parse the start and end dates for the review date range
        self.start_date = datetime.strptime(start_date, "%m/%d/%Y")
        self.end_date = datetime.strptime(end_date, "%m/%d/%Y")
        # Set the rating mean dictionary and standard deviation
        self.rating_mean_dict = rating_mean_dict or {
            2020: 1.5,
            2021: 1.9,
            2022: 2.4,
            2023: 3.1,
            2024: 4.2
        }
        self.std_dev = std_dev
        # Define prompts for generating review text based on sentiment
        self.prompts = {
            'positive': [
                f"Write a positive customer review for {self.company_name}. Mention the excellent customer support.",
                f"Write a positive customer review for {self.company_name}. Highlight the variety of plan options available.",
                f"Write a positive customer review for {self.company_name}. Praise the comprehensive coverage provided.",
                f"Write a positive customer review for {self.company_name}. Mention the affordable premiums.",
                f"Write a positive customer review for {self.company_name}. Highlight the quick claims processing.",
                f"Write a positive customer review for {self.company_name}. Appreciate the helpful customer service.",
                f"Write a positive customer review for {self.company_name}. Praise the quality of the network.",
                f"Write a positive customer review for {self.company_name}. Mention the easy access to care.",
                f"Write a positive customer review for {self.company_name}. Appreciate the user-friendly online tools.",
                f"Write a positive customer review for {self.company_name}. Mention the preventive care coverage.",
                f"Write a positive customer review for {self.company_name}. Praise the clear communication.",
                f"Write a positive customer review for {self.company_name}. Appreciate the health and wellness programs."
            ],
            'neutral': [
                f"Write a neutral customer review for {self.company_name}. Mention that the service was okay but not exceptional."
            ],
            'negative': [
                f"Write a negative customer review for {self.company_name}. Mention a bad experience with claim processing.",
                f"Write a negative customer review for {self.company_name}. Complain about the high premiums.",
                f"Write a negative customer review for {self.company_name}. Mention the terrible customer support.",
                f"Write a negative customer review for {self.company_name}. Complain about the lack of variety of plan options available.",
                f"Write a negative customer review for {self.company_name}. Complain about claim denials.",
                f"Write a negative customer review for {self.company_name}. Mention billing issues.",
                f"Write a negative customer review for {self.company_name}. Complain about coverage limitations.",
                f"Write a negative customer review for {self.company_name}. Mention negative experiences with customer service.",
                f"Write a negative customer review for {self.company_name}. Complain about network issues.",
                f"Write a negative customer review for {self.company_name}. Mention preauthorization requirements.",
                f"Write a negative customer review for {self.company_name}. Complain about policy changes.",
                f"Write a negative customer review for {self.company_name}. Mention lack of transparency.",
                f"Write a negative customer review for {self.company_name}. Complain about the appeals process."
            ]
        }
        # Set the random seed for reproducibility
        random.seed(42)

    def generate_review(self, prompt):
        # Generate a single review using the OpenAI API
        response = self.client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": f"You are a customer of {self.company_name}. Only respond with the review."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        # Return the generated review text
        return response.choices[0].message.content.strip()

    def generate_random_date(self):
        # Generate a random date within the specified date range
        delta = self.end_date - self.start_date
        random_days = random.randint(0, delta.days)
        return self.start_date + timedelta(days=random_days)

    def generate_rating(self, year):
        # Generate a rating based on the mean rating for the year and a standard deviation
        mean_rating = self.rating_mean_dict.get(year, 3)  # Default to 3 if year not in dictionary
        rating = round(random.normalvariate(mean_rating, self.std_dev))
        # Ensure the rating is within the range of 1 to 5
        return max(1, min(rating, 5))

    def generate_reviews(self):
        review_data = []

        for i in range(self.num_reviews):
            # Generate a random review date
            review_date = self.generate_random_date()
            year = review_date.year
            # Generate a rating based on the year
            rating = self.generate_rating(year)

            # Determine sentiment based on the rating
            if rating > 3:
                sentiment = 'positive'
            elif rating < 3:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            # Select a prompt based on the sentiment
            prompt = random.choice(self.prompts[sentiment])
            # Generate the review text
            review_text = self.generate_review(prompt)
            review_date_str = review_date.strftime("%Y-%m-%d")

            # Create a review dictionary with all the necessary information
            review = {
                'Review_ID': i + 1,
                'Customer_ID': random.randint(1, self.num_customers),
                'Review_Date': review_date_str,
                'Rating': rating,
                'Review_Text': review_text,
                'Sentiment': sentiment,
                'Prompt': prompt,
                'Company_Name': self.company_name
            }
            # Append the review dictionary to the review data list
            review_data.append(review)

        # Convert the review data list to a pandas DataFrame
        return pd.DataFrame(review_data)

    def save_to_csv(self, df, filename):
        # Save the DataFrame to a CSV file
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
